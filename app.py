"""Streamlit interface for the PawPal+ pet-care scheduler."""

from datetime import date, datetime, time

import streamlit as st

from pawpal_system import Owner, Pet, Scheduler, Task


st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="wide")
st.title("🐾 PawPal+")
st.caption("Keep your pets' daily care simple and organized.")

if "owner" not in st.session_state:
    st.session_state.owner = Owner("Pet Owner")

owner: Owner = st.session_state.owner
scheduler = Scheduler(owner)

with st.sidebar:
    st.header("Your profile")
    with st.form("owner_form"):
        owner_name = st.text_input("Owner name", value=owner.name)
        if st.form_submit_button("Save name"):
            if owner_name.strip():
                owner.name = owner_name.strip()
                st.success("Name saved.")
            else:
                st.error("Please enter a name.")
    st.write(f"**Pets:** {len(owner.pets)}")
    st.write(f"**Care tasks:** {len(owner.all_tasks())}")
    st.caption("Information is stored in this browser session, not in a database.")


def rows_for(tasks: list[Task]) -> list[dict]:
    """Turn task objects into readable table rows."""
    return [
        {
            "Date": task.due_date.isoformat(),
            "Time": task.time,
            "Pet": task.pet_name,
            "Task": task.description,
            "Minutes": task.duration,
            "Priority": task.priority.title(),
            "Repeats": task.frequency.title(),
            "Status": "Done" if task.completed else "Pending",
        }
        for task in tasks
    ]


def task_label(task: Task) -> str:
    """Show enough details to identify a task in a selection box."""
    return f"{task.due_date} | {task.time} | {task.pet_name} | {task.description} ({task.task_id[:5]})"


pets_tab, plan_tab, manage_tab = st.tabs(["Pets & new tasks", "Daily plan", "Manage tasks"])

with pets_tab:
    st.subheader("Add a pet")
    with st.form("add_pet", clear_on_submit=True):
        left, right, extra = st.columns(3)
        with left:
            pet_name = st.text_input("Pet name")
        with right:
            species = st.selectbox("Species", ["Dog", "Cat", "Bird", "Rabbit", "Other"])
        with extra:
            breed = st.text_input("Breed (optional)")
        if st.form_submit_button("Add pet"):
            try:
                owner.add_pet(Pet(pet_name, species, breed))
                st.success(f"Added {pet_name.strip()}!")
            except ValueError as exc:
                st.error(str(exc))

    if owner.pets:
        st.subheader("Your pets")
        st.write(" · ".join(f"**{pet.name}** ({pet.species})" for pet in owner.pets))
        st.subheader("Schedule a care task")
        with st.form("add_task", clear_on_submit=True):
            pet_selected = st.selectbox("For pet", [pet.name for pet in owner.pets])
            description = st.text_input("Activity", placeholder="Morning walk, feeding, medication...")
            col1, col2, col3 = st.columns(3)
            with col1:
                task_date = st.date_input("Date", value=date.today())
                task_time = st.time_input("Starting time", value=time(8, 0), step=900)
            with col2:
                duration = st.number_input("Duration (minutes)", min_value=1, max_value=1440, value=15)
            with col3:
                priority = st.selectbox("Priority", ["high", "medium", "low"], index=1)
                frequency = st.selectbox("Repeat", ["once", "daily", "weekly"])
            if st.form_submit_button("Add task"):
                try:
                    new_task = Task(
                        description=description,
                        time=task_time.strftime("%H:%M"),
                        due_date=task_date,
                        duration=int(duration),
                        priority=priority,
                        frequency=frequency,
                    )
                    owner.get_pet(pet_selected).add_task(new_task)
                    st.success("Task saved. Open Daily plan to see it.")
                except ValueError as exc:
                    st.error(str(exc))
    else:
        st.info("Add a pet first, then you can schedule tasks.")

with plan_tab:
    st.subheader("Daily care plan")
    selected_date = st.date_input("Plan for", value=date.today(), key="plan_date")
    use_budget = st.checkbox("Set a daily time limit", value=False)
    minutes = None
    if use_budget:
        minutes = int(st.number_input("Time available (minutes)", min_value=0, max_value=1440, value=90))
    planned, skipped = scheduler.daily_plan(selected_date, minutes)
    if planned:
        st.dataframe(rows_for(planned), use_container_width=True, hide_index=True)
        st.caption("The schedule is displayed by starting time. When time is limited, higher-priority tasks are chosen first.")
    else:
        st.info("No pending tasks in this plan yet.")
    if skipped:
        st.subheader("Tasks that did not fit")
        st.dataframe(rows_for(skipped), use_container_width=True, hide_index=True)
        st.caption("These tasks were left out because of the time limit. They are not deleted.")
    conflicts = scheduler.detect_conflicts(selected_date)
    for warning in conflicts:
        st.warning(warning)
    if not conflicts:
        st.success("No matching start-time conflicts for this date.")
    st.caption("Conflict warnings compare exact start times, not overlapping durations.")

with manage_tab:
    st.subheader("Find and update tasks")
    all_tasks = scheduler.sort_by_time()
    if all_tasks:
        filter_col1, filter_col2 = st.columns(2)
        with filter_col1:
            pet_filter = st.selectbox("Pet filter", ["All pets"] + [pet.name for pet in owner.pets])
        with filter_col2:
            status_filter = st.selectbox("Status filter", ["All tasks", "Pending", "Done"])
        filtered = scheduler.filter_tasks(
            pet_name=None if pet_filter == "All pets" else pet_filter,
            completed={"Pending": False, "Done": True}.get(status_filter),
        )
        if filtered:
            st.dataframe(rows_for(filtered), use_container_width=True, hide_index=True)
        else:
            st.info("No tasks match these filters.")

        pending = scheduler.filter_tasks(completed=False)
        if pending:
            st.subheader("Mark a task complete")
            with st.form("complete_task"):
                complete_task = st.selectbox("Choose a pending task", pending, format_func=task_label)
                if st.form_submit_button("Mark complete"):
                    next_task = scheduler.mark_task_complete(complete_task.task_id)
                    if next_task:
                        st.success(f"Completed! Next occurrence: {next_task.due_date} at {next_task.time}.")
                    else:
                        st.success("Task completed!")

        st.subheader("Edit a task")
        chosen = st.selectbox("Task to edit", all_tasks, format_func=task_label)
        with st.form(f"edit_{chosen.task_id}"):
            edit_desc = st.text_input("Activity", value=chosen.description)
            e1, e2, e3 = st.columns(3)
            with e1:
                edit_date = st.date_input("Date", value=chosen.due_date, key=f"date_{chosen.task_id}")
                edit_time = st.time_input(
                    "Starting time", value=datetime.strptime(chosen.time, "%H:%M").time(), key=f"time_{chosen.task_id}"
                )
            with e2:
                edit_duration = st.number_input(
                    "Duration", min_value=1, max_value=1440, value=chosen.duration, key=f"duration_{chosen.task_id}"
                )
            with e3:
                edit_priority = st.selectbox(
                    "Priority", ["high", "medium", "low"], index=["high", "medium", "low"].index(chosen.priority)
                )
                edit_repeat = st.selectbox(
                    "Repeat", ["once", "daily", "weekly"], index=["once", "daily", "weekly"].index(chosen.frequency)
                )
            if st.form_submit_button("Save changes"):
                try:
                    scheduler.update_task(
                        chosen.task_id, edit_desc, edit_time.strftime("%H:%M"), edit_date,
                        int(edit_duration), edit_priority, edit_repeat,
                    )
                    st.success("Changes saved!")
                except ValueError as exc:
                    st.error(str(exc))
    else:
        st.info("Add a pet and a task to start managing your schedule.")
