from database.base import (
    add_task,
    get_task,
    get_all_tasks,
    get_tasks_by_status,
    update_task_status,
    delete_task,
)
from models.models import Task


VALID_PRIORITIES = {"low", "medium", "high", "critical"}
VALID_STATUSES = {"backlog", "todo", "in_progress", "review", "done"}


def validate_task(title, description, assignee, deadline, priority):
    if not title:
        return "Название задачи не может быть пустым."

    if not description:
        return "Описание задачи не может быть пустым."

    if not assignee:
        return "Исполнитель задачи не может быть пустым."

    if not deadline:
        return "Дедлайн задачи не может быть пустым."

    if priority not in VALID_PRIORITIES:
        return (
            "Неверный приоритет.\n"
            "Доступные приоритеты: low, medium, high, critical"
        )

    return None


def row_to_task(row):
    if row is None:
        return None

    return Task(
        task_id=row[0],
        title=row[1],
        description=row[2],
        assignee=row[3],
        deadline=row[4],
        priority=row[5],
        status=row[6],
        created_at=row[7],
    )


def create_task(title, description, assignee, deadline, priority):
    error = validate_task(title, description, assignee, deadline, priority)

    if error:
        return None

    task_id = add_task(title, description, assignee, deadline, priority)

    return Task(
        task_id=task_id,
        title=title,
        description=description,
        assignee=assignee,
        deadline=deadline,
        priority=priority,
        status="backlog",
    )


def get_task_by_id(task_id):
    row = get_task(task_id)
    return row_to_task(row)


def get_all_tasks_list():
    rows = get_all_tasks()
    return [row_to_task(row) for row in rows]


def get_tasks_by_status_grouped():
    grouped_tasks = {}

    for status in ["backlog", "todo", "in_progress", "review", "done"]:
        rows = get_tasks_by_status(status)
        grouped_tasks[status] = [row_to_task(row) for row in rows]

    return grouped_tasks


def move_task(task_id, new_status):
    if new_status not in VALID_STATUSES:
        return False, (
            "Неверный статус.\n"
            "Доступные статусы: backlog, todo, in_progress, review, done"
        )

    success = update_task_status(task_id, new_status)

    if not success:
        return False, f"Задача #{task_id} не найдена."

    return True, None


def delete_task_by_id(task_id):
    return delete_task(task_id)