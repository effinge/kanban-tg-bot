from storage.storage import load_tasks, save_tasks
from models.models import make_task

def _next_id(tasks: list) -> int:
    if not tasks:
        return 1
    return max(t["id"] for t in tasks) + 1

def create_task(title: str, description: str, assignee: str, deadline: str, priority: str) -> dict:
    tasks = load_tasks()
    task = make_task(_next_id(tasks), title, description, assignee, deadline, priority)
    tasks.append(task)
    save_tasks(tasks)
    return task

def get_all_tasks() -> list:
    return load_tasks()

def get_task_by_id(task_id: int) -> dict | None:
    tasks = load_tasks()
    for task in tasks:
        if task["id"] == task_id:
            return task
    return None