from database.dbase import add_task, get_task, get_all_tasks, update_task_status
from database.dbase import add_task, get_task, get_all_tasks
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

VALID_PRIORITIES = {"low", "medium", "high"}
VALID_STATUSES = {"Backlog", "To Do", "In Progress", "Review", "Done"}


def validate_task(title, priority):
    if not title:
        return "Название не может быть пустым."
    if priority.lower() not in VALID_PRIORITIES:
        return "Приоритет должен быть: low, medium, high."
    return None


def move_task(task_id, new_status):
    if new_status not in VALID_STATUSES:
        return False, f"Неверный статус. Доступны: {', '.join(VALID_STATUSES)}"

    success = update_task_status(task_id, new_status)
    if not success:
        return False, f"Задача #{task_id} не найдена."

    return True, None