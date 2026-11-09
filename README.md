# 🐾 PawPal+ — Smart Pet Care Scheduler

PawPal+ is a Python/Streamlit app for planning pet care. It helps owners track walks, feedings, medicine, and other daily tasks. I built the main scheduling logic using four object-oriented classes and tested it separately from the UI.

## Features

- Add multiple pets and an owner name.
- Schedule or edit care activities with a date, time, duration, priority, and repeat frequency.
- View a daily plan in time order; filter by pet or completion status.
- Mark tasks complete and automatically create the next occurrence for daily or weekly tasks.
- Get a warning when two unfinished tasks have the same starting time.
- Set an optional daily time limit; higher-priority tasks are selected first and skipped tasks are shown separately.

**Storage note:** Pets and tasks are kept in `st.session_state` for the current Streamlit session. They are not saved to a database.

## Project files

| File | Purpose |
| --- | --- |
| `pawpal_system.py` | OOP classes and scheduling logic |
| `app.py` | Streamlit UI |
| `main.py` | Command-line demo |
| `tests/test_pawpal.py` | Automated pytest checks |
| `diagrams/uml_draft.mmd` | Initial system design |
| `diagrams/uml_final.mmd` | Final UML matching the code |
| `reflection.md` | Design and AI collaboration reflection |
| `ai_interactions.md` | Starter's optional stretch-feature log |

## Setup

Use Python 3.10 or newer:

```bash
python -m venv .venv
```

Windows PowerShell: ` .\.venv\Scripts\Activate.ps1 `

macOS/Linux: `source .venv/bin/activate`

Then run:

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

To verify the backend separately, run `python main.py`.

## 🖥️ Sample Output

This is an example from running `python main.py` locally on November 9, 2026. Dates are based on the day you run it.

```text
Today's Schedule - 2026-11-09
  08:00 - Biscuit: Morning walk (30 min) [high]
  08:00 - Luna: Breakfast (10 min) [high]
  12:00 - Luna: Brush fur (15 min) [low]
Skipped due to time limit:
  18:00 - Biscuit: Evening walk
Conflict warnings:
  08:00: Multiple tasks start together (Biscuit: Morning walk, Luna: Breakfast).
Next recurring task: Morning walk on 2026-11-10
```

## 📐 Smarter Scheduling

| Feature | Method | Description |
| --- | --- | --- |
| Sorting | `Scheduler.sort_by_time()` | Orders tasks by due date and start time |
| Filtering | `Scheduler.filter_tasks()` | Filters by pet name, completion, and date |
| Recurrence | `Scheduler.mark_task_complete()` / `Task.next_occurrence()` | Creates the next daily/weekly task on completion |
| Conflict detection | `Scheduler.detect_conflicts()` | Warns when tasks start at the same time |
| Priorities | `Scheduler.daily_plan()` | Picks higher-priority tasks first if time is limited |
| Editing | `Scheduler.update_task()` | Changes a task after validating its fields |

**Tradeoffs:** Conflict detection compares exact start times, not all overlapping durations. The time-limited planner uses a readable priority-first method instead of trying every task combination. Skipped tasks are displayed, not rescheduled or deleted.

## 🧪 Testing PawPal+

Run all tests with:

```bash
python -m pytest
```

The 15 tests cover task addition and completion, sorting, filtering, daily and weekly recurrence, duplicate completion prevention, conflicts, time limits, editing, invalid times, duplicate pet names, and an empty schedule.

A successful local test run produced:

```text
...............                                                          [100%]
15 passed in 0.03s
```

**Confidence: 4/5 stars.** The automated backend tests passed, but the browser interface should still be checked manually before submission.

## 📸 Demo Walkthrough

1. Run `python -m streamlit run app.py` and enter your name in the sidebar.
2. Open **Pets & new tasks** and add Biscuit (dog) and Luna (cat).
3. Add a daily morning walk for Biscuit at 08:00 and breakfast for Luna at 08:00. Add other tasks with different priorities.
4. Open **Daily plan**. Tasks appear in time order, and a warning appears for the two activities at 08:00. You can set a time limit to prioritize tasks.
5. Open **Manage tasks** to filter, edit, or mark a task complete. Completing a daily walk adds another for tomorrow.
6. Run `python main.py` to see the same scheduling logic in the terminal.

## Architecture

Four classes make up the backend: `Owner` manages pets, `Pet` contains care tasks, `Task` represents each activity, and `Scheduler` organizes and updates tasks. See the `.mmd` files in `diagrams/` for the original and final UML drawings. They can be previewed using [Mermaid Live Editor](https://mermaid.live/).

## Known limitations

Session data resets if the session is lost. There is no persistent database, automatic reminder, full duration-overlap detection, or optimal scheduling solver.
