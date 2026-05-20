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


from services.team_service import user_has_team, get_team_members_text
from services.task_service import create_task

class CallbackHandler:
    def __init__(self, bot):
        self.bot = bot

    def handle(self, callback_query):
        chat_id = callback_query["message"]["chat"]["id"]
        callback_query_id = callback_query.get("id")
        user_id = callback_query["from"]["id"]
        callback_data = callback_query["data"]

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

        elif callback_data == "show_board":
            self.show_board(chat_id)

        elif callback_data == "show_tasks":
            self.show_tasks(chat_id)

        elif callback_data == "show_members":
            self.show_members(chat_id, user_id)

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
    def show_members(self, chat_id, user_id):
        self.bot.send_message(chat_id, get_team_members_text(user_id))

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
        self.bot.send_message(
            chat_id,
            "Главное меню команды.\n\n"
            "Выбери действие:",
            reply_markup=main_menu_keyboard(),
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
