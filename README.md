TrackMe - Final Release (REPL + One-liner)
=========================================
Features:
- start (prompts for task name, category, notes)
- pause (pause active task)
- resume <id> (resume paused task by ID)
- stop (stop active task and save)
- stop <id> (stop a paused task directly and save)
- complete <id> (mark paused or active task as completed without resuming)
- viewday / viewweek / viewmonth (view includes Status column: Active/Paused/Completed)
- paused (list paused tasks)
- status (show active task)
- REPL mode: run `trackme` to enter interactive prompt
- One-liner mode: `trackme start "Task name"` etc.
- Data stored locally: ~/.trackme/trackme.db, paused.json, active.json
Installation:
1. unzip and cd into project
2. chmod +x setup_trackme.sh
3. ./setup_trackme.sh
4. source ~/.zshrc (or restart shell)
