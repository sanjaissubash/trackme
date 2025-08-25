import time, datetime
from rich.console import Console
from . import storage

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

def start_new_task_interactive():
    # start new task, pausing any active
    if storage.load_active():
        # auto-pause existing active
        pause_active()

    task_name = input('Task name: ').strip()
    if not task_name:
        print('Canceled: empty task name')
        return None
    category = input('Category: ').strip()
    notes = input('Notes: ').strip()
    tid = storage.generate_id()
    now = datetime.datetime.now().isoformat()   # <-- corrected line
    task = {
        'id': tid,
        'task_name': task_name,
        'category': category,
        'notes': notes,
        'start_time': now,
        'date': now.split('T')[0]
    }
    storage.save_active(task)
    print(f"✅ Started task: {task_name} (ID: {tid})")
    print('⏳ Tracking... use stop or pause or resume <id> to switch')
    return task

def start_new_task_quick(task_name, category='', notes=''):
    if storage.load_active():
        pause_active()
    tid = storage.generate_id()
    now = datetime.datetime.now().isoformat()
    task = {
        'id': tid,
        'task_name': task_name,
        'category': category,
        'notes': notes,
        'start_time': now,
        'date': now.split('T')[0]
    }
    storage.save_active(task)
    console.print(f"✅ Started task: {task_name} (ID: {tid})", style='green')
    console.print('⏳ Tracking... use stop or pause or resume <id> to switch', style='cyan')
    return task

def pause_active():
    active = storage.load_active()
    if not active:
        print('No active task to pause.')
        return None
    start = datetime.datetime.fromisoformat(active['start_time'])
    elapsed = int((datetime.datetime.now() - start).total_seconds())
    paused = {
        'id': active['id'],
        'task_name': active['task_name'],
        'category': active.get('category',''),
        'notes': active.get('notes',''),
        'elapsed': elapsed,
        'date': active.get('date', datetime.datetime.now().date().isoformat())
    }
    storage.add_paused(paused)
    storage.clear_active()
    console.print(f'⏸ Task paused: {paused["task_name"]} at {format_seconds(elapsed)}', style='yellow')
    return paused

def resume_task(task_id):
    p = storage.find_paused(task_id)
    if not p:
        print(f'No paused task with id {task_id}')
        return None
    if storage.load_active():
        pause_active()
    now = datetime.datetime.now()
    start = now - datetime.timedelta(seconds=p.get('elapsed',0))
    active = {
        'id': p['id'],
        'task_name': p['task_name'],
        'category': p.get('category',''),
        'notes': p.get('notes',''),
        'start_time': start.isoformat(),
        'date': p.get('date', now.date().isoformat())
    }
    storage.save_active(active)
    storage.remove_paused(task_id)
    console.print(f'▶️ Resumed: {active["task_name"]} (ID: {active["id"]})', style='blue')
    return active

def stop_active():
    active = storage.load_active()
    if not active:
        print('No active task to stop.')
        return None
    start = datetime.datetime.fromisoformat(active['start_time'])
    end = datetime.datetime.now()
    duration = int((end - start).total_seconds())
    completed = {
        'id': active['id'],
        'task_name': active['task_name'],
        'category': active.get('category',''),
        'notes': active.get('notes',''),
        'start_time': active['start_time'],
        'end_time': end.isoformat(),
        'duration': duration,
        'date': active.get('date', end.date().isoformat()),
        'status': 'completed'
    }
    storage.save_completed(completed)
    storage.clear_active()
    console.print(f"✅ Stopped task: {completed['task_name']} — Duration: {format_seconds(duration)}", style='green')
    return completed

def stop_paused(task_id):
    p = storage.find_paused(task_id)
    if not p:
        print(f'No paused task with id {task_id}')
        return None
    now = datetime.datetime.now()
    duration = int(p.get('elapsed', 0))
    start_dt = now - datetime.timedelta(seconds=duration)
    completed = {
        'id': p['id'],
        'task_name': p.get('task_name'),
        'category': p.get('category',''),
        'notes': p.get('notes',''),
        'start_time': start_dt.isoformat(),
        'end_time': now.isoformat(),
        'duration': duration,
        'date': p.get('date', now.date().isoformat()),
        'status': 'completed'
    }
    storage.save_completed(completed)
    storage.remove_paused(task_id)
    console.print(f"✅ Stopped paused task: {completed['task_name']} — Duration: {format_seconds(duration)}", style='green')
    return completed

def complete_task(task_id=None):
    # complete active if no id
    if task_id is None:
        return stop_active()
    # complete paused if exists
    p = storage.find_paused(task_id)
    if p:
        now = datetime.datetime.now()
        duration = int(p.get('elapsed', 0))
        start_dt = now - datetime.timedelta(seconds=duration)
        completed = {
            'id': p['id'],
            'task_name': p.get('task_name'),
            'category': p.get('category',''),
            'notes': p.get('notes',''),
            'start_time': start_dt.isoformat(),
            'end_time': now.isoformat(),
            'duration': duration,
            'date': p.get('date', now.date().isoformat()),
            'status': 'completed'
        }
        storage.save_completed(completed)
        storage.remove_paused(task_id)
        console.print(f"✅ Completed paused task: {completed['task_name']} — Duration: {format_seconds(duration)}", style='green')
        return completed
    # if active matches id, stop it
    active = storage.load_active()
    if active and active.get('id') == task_id:
        return stop_active()
    print(f'No paused or active task with id {task_id}')
    return None

def status():
    active = storage.load_active()
    if not active:
        print('No active task.')
        return None
    start = datetime.datetime.fromisoformat(active['start_time'])
    elapsed = int((datetime.datetime.now() - start).total_seconds())
    print(f"[Active] {active['id']} {active['task_name']} — Elapsed: {format_seconds(elapsed)}")
    return active
