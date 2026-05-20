from services.task_service import (
    get_all_tasks_list,
    get_task_by_id,
    get_tasks_by_status_grouped,
    move_task,
    delete_task_by_id,
)
from services.member_service import get_members_text
from services.stats_service import get_stats_text, get_deadlines_text
from services.formatter import (
    ADD_TASK_HELP_TEXT,
    HELP_TEXT,
    format_board,
    format_tasks_list,
)
from bot.keyboards import (
    board_keyboard,
    delete_confirm_keyboard,
    main_menu_keyboard,
    task_actions_keyboard,
    task_status_keyboard,
    tasks_keyboard,
)


class CallbackHandler:
    def __init__(self, bot):
        self.bot = bot

    def handle(self, callback_query):
        chat_id = callback_query["message"]["chat"]["id"]
        callback_query_id = callback_query.get("id")
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

        elif callback_data == "task:add_help":
            self.show_add_help(chat_id)

        elif callback_data.startswith("task:show:"):
            self.show_task(chat_id, callback_data)

        elif callback_data.startswith("task:move_menu:"):
            self.show_move_menu(chat_id, callback_data)

        elif callback_data.startswith("task:move:"):
            self.handle_move_task(chat_id, callback_data)

        elif callback_data.startswith("task:delete_confirm:"):
            self.confirm_delete(chat_id, callback_data)

        elif callback_data.startswith("task:delete:"):
            self.delete_task(chat_id, callback_data)

        else:
            self.bot.send_message(chat_id, "Неизвестное действие.")

        if callback_query_id:
            self.bot.answer_callback_query(callback_query_id)

    def show_tasks(self, chat_id):
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

    def show_board(self, chat_id):
        grouped_tasks = get_tasks_by_status_grouped()

        self.bot.send_message(
            chat_id,
            format_board(grouped_tasks),
            reply_markup=board_keyboard(),
        )

    def show_members(self, chat_id):
        self.bot.send_message(chat_id, get_members_text())

    def show_stats(self, chat_id):
        self.bot.send_message(chat_id, get_stats_text())

    def show_deadlines(self, chat_id):
        self.bot.send_message(chat_id, get_deadlines_text())

    def show_help(self, chat_id):
        self.bot.send_message(
            chat_id,
            HELP_TEXT,
            reply_markup=main_menu_keyboard(),
        )

    def show_add_help(self, chat_id):
        self.bot.send_message(chat_id, ADD_TASK_HELP_TEXT)

    def show_task(self, chat_id, callback_data):
        task_id = self._get_task_id(callback_data, "task:show:")

        if task_id is None:
            self.bot.send_message(chat_id, "Не удалось определить номер задачи.")
            return

        task = get_task_by_id(task_id)

        if task is None:
            self.bot.send_message(chat_id, f"Задача #{task_id} не найдена.")
            return

        self.bot.send_message(
            chat_id,
            task.to_text(),
            reply_markup=task_actions_keyboard(task.task_id),
        )

    def show_move_menu(self, chat_id, callback_data):
        task_id = self._get_task_id(callback_data, "task:move_menu:")

        if task_id is None:
            self.bot.send_message(chat_id, "Не удалось определить номер задачи.")
            return

        task = get_task_by_id(task_id)

        if task is None:
            self.bot.send_message(chat_id, f"Задача #{task_id} не найдена.")
            return

        self.bot.send_message(
            chat_id,
            f"Выберите новый статус для задачи #{task.task_id} {task.title}:",
            reply_markup=task_status_keyboard(task.task_id, task.status),
        )

    def handle_move_task(self, chat_id, callback_data):
        parts = callback_data.split(":")

        if len(parts) != 4 or not parts[2].isdigit():
            self.bot.send_message(chat_id, "Не удалось изменить статус задачи.")
            return

        task_id = int(parts[2])
        new_status = parts[3]
        success, error = move_task(task_id, new_status)

        if not success:
            self.bot.send_message(chat_id, error)
            return

        task = get_task_by_id(task_id)

        self.bot.send_message(
            chat_id,
            f"Задача #{task_id} перемещена в статус: {new_status}.",
        )

        if task is not None:
            self.bot.send_message(
                chat_id,
                task.to_text(),
                reply_markup=task_actions_keyboard(task.task_id),
            )

    def confirm_delete(self, chat_id, callback_data):
        task_id = self._get_task_id(callback_data, "task:delete_confirm:")

        if task_id is None:
            self.bot.send_message(chat_id, "Не удалось определить номер задачи.")
            return

        task = get_task_by_id(task_id)

        if task is None:
            self.bot.send_message(chat_id, f"Задача #{task_id} не найдена.")
            return

        self.bot.send_message(
            chat_id,
            f"Удалить задачу #{task.task_id} {task.title}?",
            reply_markup=delete_confirm_keyboard(task.task_id),
        )

    def delete_task(self, chat_id, callback_data):
        task_id = self._get_task_id(callback_data, "task:delete:")

        if task_id is None:
            self.bot.send_message(chat_id, "Не удалось определить номер задачи.")
            return

        success = delete_task_by_id(task_id)

        if not success:
            self.bot.send_message(chat_id, f"Задача #{task_id} не найдена.")
            return

        self.bot.send_message(chat_id, f"Задача #{task_id} удалена.")

    def _get_task_id(self, callback_data, prefix):
        raw_task_id = callback_data.replace(prefix, "", 1)

        if not raw_task_id.isdigit():
            return None

        return int(raw_task_id)
