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
from services.formatter import (
    ADD_TASK_HELP_TEXT,
    HELP_TEXT,
    format_board,
    format_tasks_list,
)
from bot.keyboards import (
    board_keyboard,
    main_menu_keyboard,
    task_actions_keyboard,
    tasks_keyboard,
)


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

        elif text.startswith("/addmember"):
            self.handle_add_member(chat_id, text)

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
            HELP_TEXT,
            reply_markup=main_menu_keyboard(),
        )

    def handle_menu(self, chat_id):
        self.bot.send_message(
            chat_id,
            "Главное меню бота.\n\nВыберите раздел:",
            reply_markup=main_menu_keyboard(),
        )

    def handle_add(self, chat_id, text):
        raw_data = text.replace("/add", "", 1).strip()
        parts = [part.strip() for part in raw_data.split("|")]

        if len(parts) != 5:
            self.bot.send_message(
                chat_id,
                "Неверный формат команды.\n\n" + ADD_TASK_HELP_TEXT,
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
            f"Статус: {task.status}",
            reply_markup=task_actions_keyboard(task.task_id),
        )

    def handle_tasks(self, chat_id):
        tasks = get_all_tasks_list()

        if not tasks:
            self.bot.send_message(
                chat_id,
                "Задач пока нет.",
                reply_markup=tasks_keyboard([]),
            )
            return

        self.bot.send_message(
            chat_id,
            format_tasks_list(tasks),
            reply_markup=tasks_keyboard(tasks),
        )

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

        self.bot.send_message(
            chat_id,
            task.to_text(),
            reply_markup=task_actions_keyboard(task.task_id),
        )

    def handle_board(self, chat_id):
        grouped_tasks = get_tasks_by_status_grouped()

        self.bot.send_message(
            chat_id,
            format_board(grouped_tasks),
            reply_markup=board_keyboard(),
        )

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
