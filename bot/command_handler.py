from services.task_service import (
    create_task,
    validate_task,
    get_all_tasks_list,
    get_task_by_id,
    get_tasks_by_status_grouped,
    move_task,
    delete_task_by_id,
)
from services.member_service import create_member, get_members_text
from services.stats_service import get_stats_text, get_deadlines_text


class CommandHandler:
    def __init__(self, bot):
        self.bot = bot

    def handle(self, message):
        chat_id = message["chat"]["id"]
        text = message.get("text", "")

        if text.startswith("/start"):
            self.handle_start(chat_id)

        elif text.startswith("/help"):
            self.handle_help(chat_id)

        elif text.startswith("/menu"):
            self.handle_menu(chat_id)

        elif text.startswith("/add"):
            self.handle_add(chat_id, text)

        elif text.startswith("/tasks"):
            self.handle_tasks(chat_id)

        elif text.startswith("/task"):
            self.handle_task(chat_id, text)

        elif text.startswith("/board"):
            self.handle_board(chat_id)

        elif text.startswith("/move"):
            self.handle_move(chat_id, text)

        elif text.startswith("/delete"):
            self.handle_delete(chat_id, text)
        
        elif text.startswith("/addmember"):
            self.handle_add_member(chat_id, text)

        elif text.startswith("/members"):
            self.handle_members(chat_id)

        elif text.startswith("/stats"):
            self.handle_stats(chat_id)

        elif text.startswith("/deadlines"):
            self.handle_deadlines(chat_id)

        else:
            self.bot.send_message(
                chat_id,
                "Пока такой команды нет.\nНапиши /help, чтобы посмотреть команды."
            )

    def handle_start(self, chat_id):
        self.bot.send_message(
            chat_id,
            "Привет! Я Kanban FEFU Bot.\n\n"
            "Я помогу вашей команде вести задачи по Kanban-доске.\n\n"
            "Напиши /help, чтобы посмотреть команды."
        )

    def handle_help(self, chat_id):
        self.bot.send_message(
            chat_id,
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
            "Статусы: backlog, todo, in_progress, review, done\n"
            "Приоритеты: low, medium, high, critical"
        )

    def handle_menu(self, chat_id):
        keyboard = {
            "inline_keyboard": [
                [
                    {"text": "📋 Доска", "callback_data": "show_board"},
                    {"text": "📌 Все задачи", "callback_data": "show_tasks"},
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
            "Главное меню бота.\n\nВыберите раздел:",
            reply_markup=keyboard,
        )

    def handle_add(self, chat_id, text):
        raw_data = text.replace("/add", "", 1).strip()
        parts = [part.strip() for part in raw_data.split("|")]

        if len(parts) != 5:
            self.bot.send_message(
                chat_id,
                "Неверный формат команды.\n\n"
                "Используй так:\n"
                "/add Название | Описание | Исполнитель | Дедлайн | Приоритет\n\n"
                "Пример:\n"
                "/add Сделать README | Описать запуск проекта | Иван | 20.05 | high"
            )
            return

        title, description, assignee, deadline, priority = parts

        error = validate_task(title, description, assignee, deadline, priority)

        if error:
            self.bot.send_message(chat_id, error)
            return

        task = create_task(
            title=title,
            description=description,
            assignee=assignee,
            deadline=deadline,
            priority=priority,
        )

        if task is None:
            self.bot.send_message(chat_id, "Не удалось создать задачу.")
            return

        self.bot.send_message(
            chat_id,
            "Задача создана.\n\n"
            f"#{task.task_id} {task.title}\n\n"
            f"Описание: {task.description}\n"
            f"Исполнитель: {task.assignee}\n"
            f"Дедлайн: {task.deadline}\n"
            f"Приоритет: {task.priority}\n"
            f"Статус: {task.status}"
        )

    def handle_tasks(self, chat_id):
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

    def handle_task(self, chat_id, text):
        raw = text.replace("/task", "", 1).strip()

        if not raw.isdigit():
            self.bot.send_message(
                chat_id,
                "Укажи номер задачи.\n\nПример: /task 1"
            )
            return

        task = get_task_by_id(int(raw))

        if task is None:
            self.bot.send_message(chat_id, f"Задача #{raw} не найдена.")
            return

        self.bot.send_message(chat_id, task.to_text())

    def handle_board(self, chat_id):
        grouped_tasks = get_tasks_by_status_grouped()

        titles = {
            "backlog": "📥 BACKLOG",
            "todo": "📝 TO DO",
            "in_progress": "⚙️ IN PROGRESS",
            "review": "👀 REVIEW",
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

    def handle_move(self, chat_id, text):
        raw = text.replace("/move", "", 1).strip()
        parts = raw.split()

        if len(parts) != 2:
            self.bot.send_message(
                chat_id,
                "Неверный формат.\n\n"
                "Используй:\n"
                "/move id status\n\n"
                "Пример:\n"
                "/move 1 in_progress"
            )
            return

        task_id, new_status = parts

        if not task_id.isdigit():
            self.bot.send_message(
                chat_id,
                "Укажи номер задачи.\n\nПример: /move 1 done"
            )
            return

        success, error = move_task(int(task_id), new_status)

        if not success:
            self.bot.send_message(chat_id, error)
            return

        self.bot.send_message(
            chat_id,
            f"Задача #{task_id} перемещена в статус: {new_status}."
        )

    def handle_delete(self, chat_id, text):
        raw = text.replace("/delete", "", 1).strip()

        if not raw.isdigit():
            self.bot.send_message(
                chat_id,
                "Укажи номер задачи.\n\nПример: /delete 1"
            )
            return

        success = delete_task_by_id(int(raw))

        if not success:
            self.bot.send_message(chat_id, f"Задача #{raw} не найдена.")
            return

        self.bot.send_message(chat_id, f"Задача #{raw} удалена.")
    
    def handle_add_member(self, chat_id, text):
        name = text.replace("/addmember", "", 1).strip()

        success, error = create_member(name)

        if not success:
            self.bot.send_message(chat_id, error)
            return

        self.bot.send_message(chat_id, f"Участник {name} добавлен.")

    def handle_members(self, chat_id):
        self.bot.send_message(chat_id, get_members_text())

    def handle_stats(self, chat_id):
        self.bot.send_message(chat_id, get_stats_text())

    def handle_deadlines(self, chat_id):
        self.bot.send_message(chat_id, get_deadlines_text())