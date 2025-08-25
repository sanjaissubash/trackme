import sqlite3
from pathlib import Path
import json, datetime

DB_DIR = Path.home() / '.trackme'
DB_DIR.mkdir(parents=True, exist_ok=True)
DB_FILE = DB_DIR / 'trackme.db'
PAUSED_FILE = DB_DIR / 'paused.json'
ACTIVE_FILE = DB_DIR / 'active.json'
META_FILE = DB_DIR / 'meta.json'

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.executescript("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY,
        task_name TEXT NOT NULL,
        category TEXT,
        notes TEXT,
        start_time TEXT,
        end_time TEXT,
        duration INTEGER,
        date TEXT
    );
    """)
    conn.commit()
    # ensure 'status' column exists
    cur.execute("PRAGMA table_info(tasks)")
    cols = [r[1] for r in cur.fetchall()]
    if 'status' not in cols:
        try:
            cur.execute("ALTER TABLE tasks ADD COLUMN status TEXT DEFAULT 'completed'")
            conn.commit()
        except Exception:
            pass
    # set defaults for existing rows if any
    try:
        cur.execute("UPDATE tasks SET status = 'completed' WHERE status IS NULL OR status = ''")
        conn.commit()
    except Exception:
        pass
    conn.close()
    # ensure meta exists
    if not META_FILE.exists():
        META_FILE.write_text(json.dumps({'next_id': 1}))

def _get_next_id():
    if not META_FILE.exists():
        META_FILE.write_text(json.dumps({'next_id': 1}))
    data = json.loads(META_FILE.read_text())
    nid = data.get('next_id', 1)
    data['next_id'] = nid + 1
    META_FILE.write_text(json.dumps(data))
    return nid

# Paused tasks (persisted to JSON)
def load_paused():
    if not PAUSED_FILE.exists():
        return []
    try:
        return json.loads(PAUSED_FILE.read_text())
    except Exception:
        return []

def save_paused(paused_list):
    PAUSED_FILE.write_text(json.dumps(paused_list, indent=2))

def add_paused(task):
    paused = load_paused()
    paused.append(task)
    save_paused(paused)

def remove_paused(task_id):
    paused = load_paused()
    new = [t for t in paused if t['id'] != task_id]
    save_paused(new)

def find_paused(task_id):
    paused = load_paused()
    for t in paused:
        if t['id'] == task_id:
            return t
    return None

def list_paused():
    return load_paused()

# Active task file
def save_active(task):
    ACTIVE_FILE.write_text(json.dumps(task, indent=2))

def load_active():
    if not ACTIVE_FILE.exists():
        return None
    try:
        return json.loads(ACTIVE_FILE.read_text())
    except Exception:
        return None

def clear_active():
    if ACTIVE_FILE.exists():
        ACTIVE_FILE.unlink()

# Completed tasks -> SQLite
def save_completed(task):
    """Save a completed task to SQLite. Handles schema differences and status."""
    init_db()
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    # ensure status column exists
    cur.execute("PRAGMA table_info(tasks)")
    cols = [r[1] for r in cur.fetchall()]
    if 'status' not in cols:
        try:
            cur.execute("ALTER TABLE tasks ADD COLUMN status TEXT DEFAULT 'completed'")
            conn.commit()
            cols.append('status')
        except Exception:
            pass
    # prepare insert columns
    base_cols = ['id', 'task_name', 'category', 'notes', 'start_time', 'end_time', 'duration', 'date']
    insert_cols = [c for c in base_cols if c in cols]
    values = [task.get(c) for c in insert_cols]
    if 'status' in cols and 'status' not in insert_cols:
        insert_cols.append('status')
        values.append(task.get('status', 'completed'))
    placeholders = ','.join(['?'] * len(insert_cols))
    col_list_sql = ','.join(insert_cols)
    cur.execute(f"INSERT INTO tasks ({col_list_sql}) VALUES ({placeholders})", tuple(values))
    conn.commit()
    conn.close()

def get_tasks_for_date(date_str):
    init_db()
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute('SELECT * FROM tasks WHERE date = ? ORDER BY start_time', (date_str,))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows

def get_weekly_summary(iso_date):
    import datetime
    d = datetime.date.fromisoformat(iso_date)
    start = d - datetime.timedelta(days=d.weekday())
    end = start + datetime.timedelta(days=6)
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute('SELECT date, SUM(duration) as total FROM tasks WHERE date BETWEEN ? AND ? GROUP BY date ORDER BY date', (start.isoformat(), end.isoformat()))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows

def get_monthly_summary(year, month):
    import datetime, calendar
    start = datetime.date(year, month, 1)
    last = calendar.monthrange(year, month)[1]
    end = datetime.date(year, month, last)
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute('SELECT date, SUM(duration) as total FROM tasks WHERE date BETWEEN ? AND ? GROUP BY date ORDER BY date', (start.isoformat(), end.isoformat()))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows

def generate_id():
    return _get_next_id()
