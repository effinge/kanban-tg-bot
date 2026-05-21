from database.base import (
    get_tasks_count_by_status,
    get_tasks_ordered_by_deadline,
    get_total_tasks_count,
    get_members_count,
)

from services.task_service import row_to_task


def get_stats_text():
    stats = get_tasks_count_by_status()
    total_tasks = get_total_tasks_count()
    members_count = get_members_count()

    statuses = {
        "backlog": "Backlog",
        "todo": "To Do",
        "in_progress": "In Progress",
        "review": "Review",
        "done": "Done",
    }

    result = "Статистика проекта:\n\n"

    result += f"Всего задач: {total_tasks}\n"
    result += f"Участников: {members_count}\n\n"

    result += "Задачи по статусам:\n"

    for status, title in statuses.items():
        result += f"{title}: {stats.get(status, 0)}\n"

    return result


def get_deadlines_text():
    rows = get_tasks_ordered_by_deadline()
    tasks = [row_to_task(row) for row in rows]

    if not tasks:
        return "Задач с дедлайнами пока нет."

    result = "Дедлайны задач:\n\n"

    for task in tasks:
        result += (
            f"#{task.task_id} {task.title}\n"
            f"Исполнитель: {task.assignee}\n"
            f"Дедлайн: {task.deadline}\n"
            f"Приоритет: {task.priority}\n"
            f"Статус: {task.status}\n\n"
        )

    return result