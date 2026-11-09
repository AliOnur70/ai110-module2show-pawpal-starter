"""Command-line example that checks the PawPal+ scheduling logic."""

from datetime import date

from pawpal_system import Owner, Pet, Scheduler, Task


def main() -> None:
    """Build two pets' schedules and show the algorithm results."""
    today = date.today()
    owner = Owner("Alex")
    biscuit = Pet("Biscuit", "Dog", "Golden Retriever")
    luna = Pet("Luna", "Cat", "Tabby")
    owner.add_pet(biscuit)
    owner.add_pet(luna)

    biscuit.add_task(Task("Evening walk", "18:00", today, 25, "medium", "daily"))
    biscuit.add_task(Task("Morning walk", "08:00", today, 30, "high", "daily"))
    luna.add_task(Task("Breakfast", "08:00", today, 10, "high", "daily"))
    luna.add_task(Task("Brush fur", "12:00", today, 15, "low", "weekly"))

    scheduler = Scheduler(owner)
    planned, skipped = scheduler.daily_plan(today, available_minutes=55)
    print(f"Today's Schedule - {today.isoformat()}")
    for task in planned:
        print(f"  {task.time} - {task.pet_name}: {task.description} ({task.duration} min) [{task.priority}]")
    print("Skipped due to time limit:")
    for task in skipped:
        print(f"  {task.time} - {task.pet_name}: {task.description}")
    print("Conflict warnings:")
    for warning in scheduler.detect_conflicts(today):
        print(f"  {warning}")

    next_task = scheduler.mark_task_complete(biscuit.tasks[1].task_id)
    if next_task is not None:
        print(f"Next recurring task: {next_task.description} on {next_task.due_date.isoformat()}")


if __name__ == "__main__":
    main()
