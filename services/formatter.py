HELP_TEXT = (
    "Основные команды:\n\n"
    "/start — запуск бота\n"
    "/help — помощь\n"
    "/menu — главное меню\n\n"
    "Задачи:\n"
    "/add Название | Описание | Исполнитель | Дедлайн | Приоритет — создать задачу\n"
    "/tasks — показать все задачи\n"
    "/task id — показать задачу\n"
    "/board — показать Kanban-доску\n"
    "/move id status — изменить статус задачи\n"
    "/delete id — удалить задачу\n\n"
    "Сайт IMCTech Kanban:\n"
    "/link — привязать аккаунт сайта (получить код)\n"
    "/mytasks — мои задачи с сайта\n"
    "/mydeadlines — мои дедлайны с сайта\n\n"
    "Статусы: backlog, todo, in_progress, review, done\n"
    "Приоритеты: low, medium, high, critical"
)

ADD_TASK_HELP_TEXT = (
    "Чтобы создать задачу, отправь команду в формате:\n\n"
    "/add Название | Описание | Исполнитель | Дедлайн | Приоритет\n\n"
    "Пример:\n"
    "/add Сделать README | Описать запуск проекта | Иван | 20.05 | high\n\n"
    "Приоритеты: low, medium, high, critical"
)

BOARD_TITLES = {
    "backlog": "⚪ Бэклог",
    "todo": "🔘 Нужно сделать",
    "in_progress": "🟡 В процессе",
    "review": "🔵 На проверке",
    "done": "🟢 Выполнено",
}

BOARD_STATUSES = ["backlog", "todo", "in_progress", "review", "done"]


def format_tasks_list(tasks):
    result = "Список задач:\n\n"

    for task in tasks:
        result += (
            f"#{task.task_id} {task.title}\n"
            f"Исполнитель: {task.assignee}\n"
            f"Статус: {task.status}\n"
            f"Приоритет: {task.priority}\n\n"
        )

    return result


def format_board(grouped_tasks):
    result = "Kanban-доска:\n\n"

    for status in BOARD_STATUSES:
        result += f"{BOARD_TITLES[status]}\n"

        tasks = grouped_tasks.get(status, [])

        if not tasks:
            result += "пусто\n\n"
            continue

        for task in tasks:
            result += (
                f"#{task.task_id} {task.title} — "
                f"{task.assignee} — {task.priority}\n"
            )

        result += "\n"

    return result
