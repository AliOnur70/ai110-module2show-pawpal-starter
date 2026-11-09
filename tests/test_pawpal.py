"""Automated tests for the main PawPal+ behaviors."""

from datetime import date, timedelta

import pytest

from pawpal_system import Owner, Pet, Scheduler, Task


TODAY = date(2026, 11, 8)


def setup_scheduler():
    owner = Owner("Sam")
    dog = Pet("Biscuit", "Dog")
    cat = Pet("Luna", "Cat")
    owner.add_pet(dog)
    owner.add_pet(cat)
    return Scheduler(owner), dog, cat


def test_task_completion():
    task = Task("Walk", "08:00", TODAY)
    task.mark_complete()
    assert task.completed is True


def test_add_task_to_pet():
    pet = Pet("Biscuit", "Dog")
    pet.add_task(Task("Walk", "09:00", TODAY))
    assert len(pet.tasks) == 1
    assert pet.tasks[0].pet_name == "Biscuit"


def test_sorting_by_time():
    scheduler, dog, _ = setup_scheduler()
    dog.add_task(Task("Dinner", "18:00", TODAY))
    dog.add_task(Task("Breakfast", "08:00", TODAY))
    assert [task.description for task in scheduler.sort_by_time()] == ["Breakfast", "Dinner"]


def test_filter_by_pet_and_completion_status():
    scheduler, dog, cat = setup_scheduler()
    dog.add_task(Task("Dog walk", "09:00", TODAY))
    cat.add_task(Task("Cat meal", "10:00", TODAY, completed=True))
    assert [task.description for task in scheduler.filter_tasks(pet_name="biscuit")] == ["Dog walk"]
    assert [task.description for task in scheduler.filter_tasks(completed=True)] == ["Cat meal"]
    assert len(scheduler.filter_tasks(completed=False)) == 1


def test_daily_recurrence_creates_next_day():
    scheduler, dog, _ = setup_scheduler()
    task = Task("Breakfast", "08:00", TODAY, frequency="daily")
    dog.add_task(task)
    next_task = scheduler.mark_task_complete(task.task_id)
    assert task.completed is True
    assert next_task is not None
    assert next_task.due_date == TODAY + timedelta(days=1)
    assert next_task.completed is False
    assert next_task.task_id != task.task_id
    assert len(dog.tasks) == 2


def test_weekly_recurrence_creates_next_week():
    scheduler, dog, _ = setup_scheduler()
    task = Task("Grooming", "14:00", TODAY, frequency="weekly")
    dog.add_task(task)
    assert scheduler.mark_task_complete(task.task_id).due_date == TODAY + timedelta(days=7)


def test_once_task_does_not_repeat():
    scheduler, dog, _ = setup_scheduler()
    task = Task("Vet visit", "14:00", TODAY)
    dog.add_task(task)
    assert scheduler.mark_task_complete(task.task_id) is None
    assert len(dog.tasks) == 1


def test_completing_twice_does_not_duplicate_task():
    scheduler, dog, _ = setup_scheduler()
    task = Task("Walk", "08:00", TODAY, frequency="daily")
    dog.add_task(task)
    scheduler.mark_task_complete(task.task_id)
    scheduler.mark_task_complete(task.task_id)
    assert len(dog.tasks) == 2


def test_conflicts_detected_across_pets():
    scheduler, dog, cat = setup_scheduler()
    dog.add_task(Task("Walk", "08:00", TODAY))
    cat.add_task(Task("Meal", "08:00", TODAY))
    warnings = scheduler.detect_conflicts(TODAY)
    assert len(warnings) == 1
    assert "08:00" in warnings[0]
    assert "Biscuit" in warnings[0]
    assert "Luna" in warnings[0]


def test_no_conflicts_for_different_days():
    scheduler, dog, cat = setup_scheduler()
    dog.add_task(Task("Walk", "08:00", TODAY))
    cat.add_task(Task("Meal", "08:00", TODAY + timedelta(days=1)))
    assert scheduler.detect_conflicts(TODAY) == []


def test_time_budget_prefers_high_priority():
    scheduler, dog, _ = setup_scheduler()
    dog.add_task(Task("Play", "07:00", TODAY, duration=25, priority="low"))
    dog.add_task(Task("Medicine", "09:00", TODAY, duration=15, priority="high"))
    chosen, skipped = scheduler.daily_plan(TODAY, available_minutes=20)
    assert [task.description for task in chosen] == ["Medicine"]
    assert [task.description for task in skipped] == ["Play"]


def test_no_tasks_returns_empty_results():
    scheduler, _, _ = setup_scheduler()
    assert scheduler.daily_plan(TODAY) == ([], [])
    assert scheduler.detect_conflicts(TODAY) == []


def test_invalid_time_is_rejected():
    with pytest.raises(ValueError, match="HH:MM"):
        Task("Walk", "25:00", TODAY)


def test_edit_task_updates_fields():
    scheduler, dog, _ = setup_scheduler()
    task = Task("Walk", "08:00", TODAY)
    dog.add_task(task)
    updated = scheduler.update_task(task.task_id, "Long walk", "08:30", TODAY, 30, "high", "weekly")
    assert updated.description == "Long walk"
    assert updated.time == "08:30"
    assert updated.frequency == "weekly"


def test_duplicate_pet_name_rejected():
    owner = Owner("Sam")
    owner.add_pet(Pet("Luna", "Cat"))
    with pytest.raises(ValueError):
        owner.add_pet(Pet("luna", "Dog"))
