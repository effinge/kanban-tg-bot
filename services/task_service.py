from models.models import Task
from storage.storage import load_tasks, save_tasks


def _next_id(tasks):
    if not tasks:
        return 1
    return max(t["task_id"] for t in tasks) + 1


def create_task(title, description, assignee, deadline, priority):
    tasks = load_tasks()

    task = Task(
        task_id=_next_id(tasks),
        title=title,
        description=description,
        assignee=assignee,
        deadline=deadline,
        priority=priority,
    )

    tasks.append(vars(task))
    save_tasks(tasks)
    return task


def get_all_tasks():
    return load_tasks()


def get_task_by_id(task_id):
    tasks = load_tasks()
    for t in tasks:
        if t["task_id"] == task_id:
            return t
    return None