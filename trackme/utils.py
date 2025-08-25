from rich.table import Table
from rich.console import Console
from rich import box
from . import storage
import datetime

console = Console()

def format_seconds(s):
    if not s:
        return '0s'
    m, sec = divmod(int(s), 60)
    h, m = divmod(m, 60)
    parts = []
    if h:
        parts.append(f"{h}h")
    if m:
        parts.append(f"{m}m")
    if sec and not h:
        parts.append(f"{sec}s")
    return ' '.join(parts) if parts else '0s'

def print_tasks_table(rows):
    table = Table(title="Tasks for the day", box=box.SIMPLE_HEAVY)
    table.add_column("ID", justify="right")
    table.add_column("Task")
    table.add_column("Category")
    table.add_column("Status")
    table.add_column("Start")
    table.add_column("End")
    table.add_column("Duration")
    table.add_column("Notes")
    for r in rows:
        start_short = r.get('start_time','')[11:19] if r.get('start_time') else ''
        end_short = r.get('end_time','')[11:19] if r.get('end_time') else ''
        dur = format_seconds(r.get('duration',0))
        status = (r.get('status') or 'completed').lower()
        if status == 'active':
            status_display = '[green]Active[/green]'
        elif status == 'paused':
            status_display = '[yellow]Paused[/yellow]'
        else:
            status_display = '[blue]Completed[/blue]'
        table.add_row(str(r.get('id')), r.get('task_name',''), r.get('category','') or '', status_display, start_short, end_short, dur, r.get('notes','') or '')
    console.print(table)
    total = sum([r.get('duration',0) for r in rows])
    console.print(f"[bold]Total: {format_seconds(total)}[/bold]")

def show_paused():
    paused = storage.list_paused()
    if not paused:
        print('No paused tasks.')
        return
    table = Table(title='Paused Tasks')
    table.add_column('ID', justify='right')
    table.add_column('Task')
    table.add_column('Category')
    table.add_column('Elapsed')
    table.add_column('Notes')
    for p in paused:
        table.add_row(str(p['id']), p.get('task_name',''), p.get('category','') or '', format_seconds(p.get('elapsed',0)), p.get('notes','') or '')
    console.print(table)

def view_day(date_str=''):
    import datetime as _dt
    if not date_str:
        date_str = _dt.date.today().isoformat()

    # 1) Completed tasks from SQLite
    rows = storage.get_tasks_for_date(date_str)
    for r in rows:
        if 'status' not in r or not r.get('status'):
            r['status'] = 'completed'

    # 2) Paused tasks
    paused = storage.list_paused()
    for p in paused:
        if p.get('date') == date_str:
            rows.append({
                'id': p.get('id'),
                'task_name': p.get('task_name'),
                'category': p.get('category',''),
                'start_time': p.get('start_time',''),
                'end_time': '',
                'duration': int(p.get('elapsed',0)),
                'notes': p.get('notes','') or '',
                'status': 'paused'
            })

    # 3) Active task
    active = storage.load_active()
    if active and active.get('date') == date_str:
        start = _dt.datetime.fromisoformat(active['start_time'])
        elapsed = int((_dt.datetime.now() - start).total_seconds())
        rows.append({
            'id': active.get('id'),
            'task_name': active.get('task_name'),
            'category': active.get('category',''),
            'start_time': active.get('start_time'),
            'end_time': '',
            'duration': elapsed,
            'notes': active.get('notes','') or '',
            'status': 'active'
        })

    # sort chronologically
    def _sort_key(r):
        st = r.get('start_time') or ''
        return (st, r.get('id', 0))
    rows_sorted = sorted(rows, key=_sort_key)
    print_tasks_table(rows_sorted)

def view_week(date_str=''):
    import datetime
    if not date_str:
        date_str = datetime.date.today().isoformat()
    rows = storage.get_weekly_summary(date_str)
    if not rows:
        print('No data for this week.')
        return
    table = Table(title=f'Week summary')
    table.add_column('Date')
    table.add_column('Total (seconds)', justify='right')
    for r in rows:
        table.add_row(r['date'], str(r.get('total') or 0))
    console.print(table)

def view_month(year=None, month=None):
    import datetime
    if not year or not month:
        today = datetime.date.today()
        year = today.year
        month = today.month
    rows = storage.get_monthly_summary(year, month)
    if not rows:
        print('No data for this month.') 
        return
    table = Table(title=f'Month summary {year}-{month:02d}')
    table.add_column('Date')
    table.add_column('Total (seconds)', justify='right')
    for r in rows:
        table.add_row(r['date'], str(r.get('total') or 0))
    console.print(table)
