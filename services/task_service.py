from database.base import add_task, get_task, get_all_tasks
from models.models import Task


def create_task(title, description, assignee, deadline, priority):
    task_id = add_task(title, description, assignee, deadline, priority)

    return Task(
        task_id=task_id,
        title=title,
        description=description,
        assignee=assignee,
        deadline=deadline,
        priority=priority,
    )


def get_task_by_id(task_id):
    row = get_task(task_id)
    if row is None:
        return None

    return {
        "task_id": row[0],
        "title": row[1],
        "description": row[2],
        "assignee": row[3],
        "deadline": row[4],
        "priority": row[5],
        "status": row[6],
        "created_at": row[7],
    }


def get_all_tasks_list():
    rows = get_all_tasks()
    return [
        {
            "task_id": row[0],
            "title": row[1],
            "description": row[2],
            "assignee": row[3],
            "deadline": row[4],
            "priority": row[5],
            "status": row[6],
            "created_at": row[7],
        }
        for row in rows
    ]