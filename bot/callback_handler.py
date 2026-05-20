from services.task_service import (
    get_all_tasks_list,
    get_tasks_by_status_grouped,
)

from services.team_service import user_has_team, get_team_members_text
from services.task_service import create_task

class CallbackHandler:
    def __init__(self, bot):
        self.bot = bot

    def handle(self, callback_query):
        chat_id = callback_query["message"]["chat"]["id"]
        user_id = callback_query["from"]["id"]
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
            
        if callback_data == "create_team":
            self.start_create_team(chat_id, user_id)

        elif callback_data == "join_team":
            self.start_join_team(chat_id, user_id)

        elif callback_data == "show_start_help":
            self.show_start_help(chat_id)

        elif callback_data == "main_menu":
            self.show_main_menu(chat_id)

        elif callback_data == "add_task":
            self.start_add_task(chat_id, user_id)

        elif callback_data.startswith("priority_"):
            self.finish_task_with_priority(chat_id, user_id, callback_data)

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

    def show_members(self, chat_id, user_id):
        self.bot.send_message(chat_id, get_team_members_text(user_id))

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

    def start_create_team(self, chat_id, user_id):
        self.bot.user_states[user_id] = {
            "action": "create_team",
        }

        self.bot.send_message(
            chat_id,
            "Введи название команды.\n\n"
            "Например:\n"
            "IMCTech Team"
        )


    def start_join_team(self, chat_id, user_id):
        self.bot.user_states[user_id] = {
            "action": "join_team",
        }

        self.bot.send_message(
            chat_id,
            "Введи код команды из 6 символов.\n\n"
            "Например:\n"
            "A1B2C3"
        )


    def show_start_help(self, chat_id):
        self.bot.send_message(
            chat_id,
            "Как начать работу:\n\n"
            "1. Один участник создаёт команду.\n"
            "2. Бот выдаёт код из 6 символов.\n"
            "3. Остальные участники присоединяются по этому коду.\n"
            "4. После этого вся работа с доской идёт через кнопки."
        )


    def show_main_menu(self, chat_id):
        keyboard = {
            "inline_keyboard": [
                [
                    {"text": "➕ Создать задачу", "callback_data": "add_task"},
                ],
                [
                    {"text": "📋 Все задачи", "callback_data": "show_tasks"},
                    {"text": "🧱 Доска", "callback_data": "show_board"},
                ],
                [
                    {"text": "👥 Участники", "callback_data": "show_members"},
                    {"text": "📊 Статистика", "callback_data": "show_stats"},
                ],
                [
                    {"text": "⏰ Дедлайны", "callback_data": "show_deadlines"},
                    {"text": "❓ Помощь", "callback_data": "show_help"},
                ],
            ]
        }

        self.bot.send_message(
            chat_id,
            "Главное меню команды.\n\n"
            "Выбери действие:",
            reply_markup=keyboard,
        )


    def start_add_task(self, chat_id, user_id):
        if not user_has_team(user_id):
            self.bot.send_message(
                chat_id,
                "Сначала создай команду или присоединись к ней через /start."
            )
            return

        self.bot.user_states[user_id] = {
            "action": "add_task",
            "step": "title",
            "data": {},
        }

        self.bot.send_message(
            chat_id,
            "Создание задачи.\n\n"
            "Введи название задачи:"
        )
    
    def finish_task_with_priority(self, chat_id, user_id, callback_data):
        state = self.bot.user_states.get(user_id)

        if state is None or state.get("action") != "add_task":
            self.bot.send_message(chat_id, "Нет активного создания задачи.")
            return

        priority = callback_data.replace("priority_", "", 1)
        data = state["data"]

        task = create_task(
            title=data["title"],
            description=data["description"],
            assignee=data["assignee"],
            deadline=data["deadline"],
            priority=priority,
        )

        del self.bot.user_states[user_id]

        keyboard = {
            "inline_keyboard": [
                [
                    {"text": "🧱 Открыть доску", "callback_data": "show_board"},
                    {"text": "📋 Все задачи", "callback_data": "show_tasks"},
                ],
                [
                    {"text": "🏠 Главное меню", "callback_data": "main_menu"},
                ],
            ]
        }

        self.bot.send_message(
            chat_id,
            "Задача создана!\n\n"
            f"#{task.task_id} {task.title}\n"
            f"Исполнитель: {task.assignee}\n"
            f"Дедлайн: {task.deadline}\n"
            f"Приоритет: {task.priority}\n"
            f"Статус: {task.status}",
            reply_markup=keyboard,
        )