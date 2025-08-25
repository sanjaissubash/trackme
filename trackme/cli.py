import sys
from . import tracker, utils, storage

HELP_TEXT = """TrackMe - interactive mode (commands)
Commands:
  start [optional task name]   Start a task (prompts if name not provided)
  pause                        Pause active task
  resume <id>                  Resume paused task by ID
  stop [<id>]                  Stop active task or stop a paused task by id
  complete [<id>]              Mark a paused or active task as completed (without resuming)
  status                       Show active task status
  viewday [YYYY-MM-DD]         Show tasks for day (default today)
  viewweek [YYYY-MM-DD]        Show weekly summary (week of date)
  viewmonth [YYYY MM]          Show monthly summary
  paused                       List paused tasks
  help                         Show this help
  exit                         Quit
"""

def _one_liner(args):
    if not args:
        return False
    cmd = args[0]
    if cmd == 'start':
        name = ' '.join(args[1:]).strip() or None
        if name:
            tracker.start_new_task_quick(name)
        else:
            tracker.start_new_task_interactive()
        return True
    if cmd == 'stop':
        if len(args) >= 2:
            try:
                tid = int(args[1])
                tracker.stop_paused(tid)
            except Exception:
                print('ID must be a number')
        else:
            tracker.stop_active()
        return True
    if cmd == 'pause':
        tracker.pause_active()
        return True
    if cmd == 'resume':
        if len(args) < 2:
            print('Usage: trackme resume <id>')
            return True
        try:
            tid = int(args[1])
            tracker.resume_task(tid)
        except:
            print('ID must be a number')
        return True
    if cmd == 'complete':
        if len(args) >= 2:
            try:
                tid = int(args[1])
                tracker.complete_task(tid)
            except:
                print('ID must be a number')
        else:
            tracker.complete_task(None)
        return True
    if cmd == 'status':
        tracker.status()
        return True
    if cmd == 'viewday':
        dt = args[1] if len(args) > 1 else ''
        utils.view_day(dt)
        return True
    if cmd == 'viewweek':
        dt = args[1] if len(args) > 1 else ''
        utils.view_week(dt)
        return True
    if cmd == 'viewmonth':
        if len(args) >= 3:
            try:
                y = int(args[1]); m = int(args[2])
                utils.view_month(y,m)
            except:
                print('Usage: trackme viewmonth YEAR MONTH')
        else:
            utils.view_month()
        return True
    return False

def repl():
    print('🎯 TrackMe Interactive Mode — type help for commands, exit to quit')
    try:
        while True:
            line = input('>> ').strip()
            if not line:
                continue
            parts = line.split()
            cmd = parts[0].lower()
            args = parts[1:]
            if cmd == 'help':
                print(HELP_TEXT)
            elif cmd == 'start':
                name = ' '.join(args).strip() or None
                tracker.start_new_task_quick(name) if name else tracker.start_new_task_interactive()
            elif cmd == 'pause':
                tracker.pause_active()
            elif cmd == 'resume':
                if not args:
                    print('Usage: resume <id>')
                    continue
                try:
                    tid = int(args[0])
                    tracker.resume_task(tid)
                except:
                    print('ID must be number')
                    continue
            elif cmd == 'stop':
                if args:
                    try:
                        tid = int(args[0])
                        tracker.stop_paused(tid)
                    except:
                        print('ID must be a number')
                else:
                    tracker.stop_active()
            elif cmd == 'complete':
                if args:
                    try:
                        tid = int(args[0])
                        tracker.complete_task(tid)
                    except:
                        print('ID must be a number')
                else:
                    tracker.complete_task(None)
            elif cmd == 'status':
                tracker.status()
            elif cmd == 'paused':
                utils.show_paused()
            elif cmd == 'viewday':
                dt = args[0] if args else ''
                utils.view_day(dt)
            elif cmd == 'viewweek':
                dt = args[0] if args else ''
                utils.view_week(dt)
            elif cmd == 'viewmonth':
                if len(args) >= 2:
                    try:
                        y = int(args[0]); m = int(args[1])
                        utils.view_month(y,m)
                    except:
                        print('Usage: viewmonth YEAR MONTH')
                else:
                    utils.view_month()
            elif cmd in ('exit','quit'):
                print('👋 Goodbye!')
                break
            else:
                print('Unknown command. Type help for commands.')
    except (EOFError, KeyboardInterrupt):
        print('\n👋 Goodbye!')

def main():
    storage.init_db()
    if len(sys.argv) > 1:
        _one_liner(sys.argv[1:])
    else:
        repl()

if __name__ == '__main__':
    main()
