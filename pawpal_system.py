"""Core classes and scheduling logic for PawPal+."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import date, datetime, timedelta
from typing import Iterable
from uuid import uuid4


PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}
FREQUENCIES = {"once", "daily", "weekly"}


@dataclass
class Task:
    """A care activity for one pet."""

    description: str
    time: str
    due_date: date
    duration: int = 15
    priority: str = "medium"
    frequency: str = "once"
    completed: bool = False
    pet_name: str = ""
    task_id: str = field(default_factory=lambda: uuid4().hex[:12])

    def __post_init__(self) -> None:
        """Check task details before saving them."""
        self.description = self.description.strip()
        if not self.description:
            raise ValueError("Task description cannot be empty.")
        try:
            parsed = datetime.strptime(self.time, "%H:%M")
            if parsed.strftime("%H:%M") != self.time:
                raise ValueError
        except ValueError as exc:
            raise ValueError("Time must use 24-hour HH:MM format.") from exc
        if isinstance(self.due_date, datetime) or not isinstance(self.due_date, date):
            raise ValueError("Due date must be a date.")
        if not isinstance(self.duration, int) or isinstance(self.duration, bool) or self.duration <= 0:
            raise ValueError("Duration must be a positive number of minutes.")
        self.priority = self.priority.lower().strip()
        self.frequency = self.frequency.lower().strip()
        if self.priority not in PRIORITY_ORDER:
            raise ValueError("Priority must be high, medium, or low.")
        if self.frequency not in FREQUENCIES:
            raise ValueError("Frequency must be once, daily, or weekly.")

    def mark_complete(self) -> None:
        """Set this task's completion status to true."""
        self.completed = True

    def next_occurrence(self) -> Task | None:
        """Return the next recurring task, if applicable."""
        days = {"daily": 1, "weekly": 7}.get(self.frequency)
        if days is None:
            return None
        return replace(
            self,
            due_date=self.due_date + timedelta(days=days),
            completed=False,
            task_id=uuid4().hex[:12],
        )


@dataclass
class Pet:
    """A pet and the care tasks assigned to it."""

    name: str
    species: str
    breed: str = ""
    tasks: list[Task] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Ensure each pet has a name and species."""
        self.name = self.name.strip()
        self.species = self.species.strip()
        self.breed = self.breed.strip()
        if not self.name or not self.species:
            raise ValueError("Pet name and species are required.")

    def add_task(self, task: Task) -> None:
        """Assign a task to this pet."""
        if any(existing.task_id == task.task_id for existing in self.tasks):
            raise ValueError("This task has already been added.")
        if task.pet_name and task.pet_name.casefold() != self.name.casefold():
            raise ValueError("This task belongs to a different pet.")
        task.pet_name = self.name
        self.tasks.append(task)

    def find_task(self, task_id: str) -> Task | None:
        """Find one of this pet's tasks by ID."""
        return next((task for task in self.tasks if task.task_id == task_id), None)


@dataclass
class Owner:
    """A person who manages one or more pets."""

    name: str
    pets: list[Pet] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Require the owner's name."""
        self.name = self.name.strip()
        if not self.name:
            raise ValueError("Owner name cannot be empty.")

    def add_pet(self, pet: Pet) -> None:
        """Add a pet, without repeating an existing name."""
        if self.get_pet(pet.name) is not None:
            raise ValueError("A pet with this name already exists.")
        self.pets.append(pet)

    def get_pet(self, name: str) -> Pet | None:
        """Find a pet by name, ignoring capitalization."""
        return next((pet for pet in self.pets if pet.name.casefold() == name.casefold()), None)

    def all_tasks(self) -> list[Task]:
        """Collect tasks from every pet."""
        return [task for pet in self.pets for task in pet.tasks]


class Scheduler:
    """Sort, filter, plan, and update pet-care tasks."""

    def __init__(self, owner: Owner) -> None:
        """Use one owner's pets as the scheduling data source."""
        self.owner = owner

    def sort_by_time(self, tasks: Iterable[Task] | None = None) -> list[Task]:
        """Return tasks in chronological order."""
        source = self.owner.all_tasks() if tasks is None else list(tasks)
        return sorted(source, key=lambda task: (task.due_date, task.time, PRIORITY_ORDER[task.priority]))

    def filter_tasks(
        self,
        pet_name: str | None = None,
        completed: bool | None = None,
        on_date: date | None = None,
    ) -> list[Task]:
        """Find tasks matching an optional pet, status, and date."""
        tasks = self.owner.all_tasks()
        if pet_name:
            tasks = [task for task in tasks if task.pet_name.casefold() == pet_name.casefold()]
        if completed is not None:
            tasks = [task for task in tasks if task.completed == completed]
        if on_date is not None:
            tasks = [task for task in tasks if task.due_date == on_date]
        return self.sort_by_time(tasks)

    def mark_task_complete(self, task_id: str) -> Task | None:
        """Complete a task and create its next daily/weekly occurrence."""
        for pet in self.owner.pets:
            task = pet.find_task(task_id)
            if task is None:
                continue
            if task.completed:
                return None
            task.mark_complete()
            next_task = task.next_occurrence()
            if next_task is not None:
                pet.add_task(next_task)
            return next_task
        raise ValueError("Task not found.")

    def update_task(
        self,
        task_id: str,
        description: str,
        time: str,
        due_date: date,
        duration: int,
        priority: str,
        frequency: str,
    ) -> Task:
        """Validate and save edits to an existing task."""
        for task in self.owner.all_tasks():
            if task.task_id == task_id:
                candidate = Task(
                    description=description,
                    time=time,
                    due_date=due_date,
                    duration=duration,
                    priority=priority,
                    frequency=frequency,
                    completed=task.completed,
                    pet_name=task.pet_name,
                    task_id=task.task_id,
                )
                task.description = candidate.description
                task.time = candidate.time
                task.due_date = candidate.due_date
                task.duration = candidate.duration
                task.priority = candidate.priority
                task.frequency = candidate.frequency
                return task
        raise ValueError("Task not found.")

    def detect_conflicts(self, on_date: date) -> list[str]:
        """Warn when unfinished tasks have the same starting time."""
        times: dict[str, list[Task]] = {}
        for task in self.filter_tasks(completed=False, on_date=on_date):
            times.setdefault(task.time, []).append(task)
        warnings = []
        for start_time, group in sorted(times.items()):
            if len(group) > 1:
                labels = ", ".join(f"{task.pet_name}: {task.description}" for task in group)
                warnings.append(f"{start_time}: Multiple tasks start together ({labels}).")
        return warnings

    def daily_plan(self, on_date: date, available_minutes: int | None = None) -> tuple[list[Task], list[Task]]:
        """Prefer important tasks when a daily time budget is provided."""
        if available_minutes is not None and available_minutes < 0:
            raise ValueError("Available time cannot be negative.")
        tasks = self.filter_tasks(completed=False, on_date=on_date)
        if available_minutes is None:
            return tasks, []
        candidates = sorted(tasks, key=lambda task: (PRIORITY_ORDER[task.priority], task.time))
        selected, skipped = [], []
        remaining = available_minutes
        for task in candidates:
            if task.duration <= remaining:
                selected.append(task)
                remaining -= task.duration
            else:
                skipped.append(task)
        return self.sort_by_time(selected), self.sort_by_time(skipped)
