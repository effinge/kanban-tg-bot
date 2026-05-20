from services.task_service import (
    get_all_tasks_list,
    get_tasks_by_status_grouped,
)


class CallbackHandler:
    def __init__(self, bot):
        self.bot = bot

    def handle(self, callback_query):
        chat_id = callback_query["message"]["chat"]["id"]
        callback_data = callback_query["data"]

        if callback_data == "show_board":
            self.show_board(chat_id)

        elif callback_data == "show_tasks":
            self.show_tasks(chat_id)

        elif callback_data == "show_members":
            self.show_members(chat_id)

        elif callback_data == "show_stats":
            self.show_stats(chat_id)

        elif callback_data == "show_deadlines":
            self.show_deadlines(chat_id)

        elif callback_data == "show_help":
            self.show_help(chat_id)

        else:
            self.bot.send_message(chat_id, "Неизвестное действие.")

    def show_tasks(self, chat_id):
        tasks = get_all_tasks_list()

        if not tasks:
            self.bot.send_message(chat_id, "Задач пока нет.")
            return

        result = "Список задач:\n\n"

        for task in tasks:
            result += (
                f"#{task.task_id} {task.title}\n"
                f"Исполнитель: {task.assignee}\n"
                f"Статус: {task.status}\n"
                f"Приоритет: {task.priority}\n\n"
            )

        self.bot.send_message(chat_id, result)

    def show_board(self, chat_id):
        grouped_tasks = get_tasks_by_status_grouped()

        titles = {
            "backlog": "📦 BACKLOG",
            "todo": "📝 TO DO",
            "in_progress": "⚙️ IN PROGRESS",
            "review": "🔍 REVIEW",
            "done": "✅ DONE",
        }

        result = "Kanban-доска:\n\n"

        for status in ["backlog", "todo", "in_progress", "review", "done"]:
            result += f"{titles[status]}\n"

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

        self.bot.send_message(chat_id, result)

    def show_members(self, chat_id):
        self.bot.send_message(
            chat_id,
            "Раздел «Участники» будет добавлен следующим этапом.\n\n"
            "Позже здесь можно будет посмотреть участников команды."
        )

    def show_stats(self, chat_id):
        self.bot.send_message(
            chat_id,
            "Раздел «Статистика» будет добавлен следующим этапом.\n\n"
            "Позже здесь будет количество задач по статусам."
        )

    def show_deadlines(self, chat_id):
        self.bot.send_message(
            chat_id,
            "Раздел «Дедлайны» будет добавлен следующим этапом.\n\n"
            "Позже здесь будут ближайшие дедлайны задач."
        )

    def show_help(self, chat_id):
        self.bot.send_message(
            chat_id,
            "Помощь по Kanban Bot:\n\n"
            "/start — запуск бота\n"
            "/help — помощь\n"
            "/menu — главное меню\n\n"
            "Работа с задачами:\n"
            "/add Название | Описание | Исполнитель | Дедлайн | Приоритет — создать задачу\n"
            "/tasks — показать все задачи\n"
            "/task id — показать одну задачу\n"
            "/board — показать Kanban-доску\n"
            "/move id status — изменить статус задачи\n"
            "/delete id — удалить задачу\n\n"
            "Статусы:\n"
            "backlog, todo, in_progress, review, done\n\n"
            "Приоритеты:\n"
            "low, medium, high, critical"
        )