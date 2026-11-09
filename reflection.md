# PawPal+ Project Reflection

*Draft reflection based on this project's design and tests. Review and edit to reflect your own experience before submitting.*

## 1. System Design

**a. Initial design**

Three important actions are adding a pet, scheduling a care task, and viewing the daily plan. The design uses four classes: `Owner`, `Pet`, `Task`, and `Scheduler`. `Owner` holds pets, `Pet` holds tasks, `Task` stores the details of an activity, and `Scheduler` finds and organizes tasks. The draft Mermaid diagram shows how they are connected.

**b. Design changes**

The basic design was extended with duration, priority, repeat frequency, and a unique task ID. These fields help the scheduler choose tasks, repeat them, and update the correct one. The final UML shows these extra fields and methods without adding unnecessary classes.

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler uses dates, start times, duration, completion status, and priority. It sorts tasks by their scheduled time. If a user sets a time limit, the scheduler considers high-priority tasks first and only selects tasks that fit the remaining minutes.

**b. Tradeoffs**

Conflict warnings check whether unfinished tasks start at exactly the same time. This is simple and readable, but a walk from 08:00 to 08:30 and a feeding at 08:15 would not be flagged. A later version could check for overlapping durations. The priority-first planner is also simpler than finding the mathematically best task combination.

## 3. AI Collaboration

**a. How AI was used**

ChatGPT was used to plan the four-class design, generate the Python implementation, create UML diagrams, and draft the test suite and documentation. Requests about class responsibilities, daily task repetition, and which edge cases to check were useful.

**b. Judgment and verification**

One simpler design choice was checking exact task start times instead of building full duration-overlap detection. This approach matches the basic project scope, though it has a documented limitation. The code was checked by running `main.py` and automated tests. The Streamlit UI still needs a hands-on browser review.

## 4. Testing and Verification

**a. What was tested**

The 15 automated checks cover adding and completing tasks, sorting, filtering, recurring dates, duplicate completion, conflicts, time limits, editing, invalid time input, duplicate pet names, and empty schedules. These tests check both common actions and some mistakes a user could make.

**b. Confidence**

The backend has a **4 out of 5** confidence rating because the automated tests passed. Further testing should include Streamlit forms, sessions restarting, unusually large schedules, and durations that overlap but have different starting times.

## 5. Reflection

**a. What went well**

The backend is separated from the Streamlit interface and can be exercised from a terminal. This makes it easier to debug the scheduler without relying on the website.

**b. What to improve**

A database would keep pets and tasks saved between sessions. Reminders and full overlapping-time checks would make the application more helpful.

**c. Key takeaway**

AI can speed up software development, but understanding class responsibilities, testing the code, and documenting tradeoffs are still important. The main classes and methods should be clear enough for a developer to explain and maintain.
