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
from services.team_service import create_team, join_team
from services import site_api
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
    task_priority_keyboard,
)


class CommandHandler:
    def __init__(self, bot):
        self.bot = bot

    def handle(self, message):
        chat_id = message["chat"]["id"]
        user_id = message["from"]["id"]
        text = message.get("text", "")

        if user_id in self.bot.user_states and not text.startswith("/"):
            self.handle_user_state(message)
            return
        
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

        elif text.startswith("/mydeadlines"):
            self.handle_my_deadlines(chat_id, user_id)

        elif text.startswith("/mytasks"):
            self.handle_my_tasks(chat_id, user_id)

        elif text.startswith("/link"):
            self.handle_link(chat_id, user_id, message["from"].get("username"))

        elif text.startswith("/deadlines"):
            self.handle_deadlines(chat_id)

        else:
            self.bot.send_message(
                chat_id,
                "Пока такой команды нет.\nНапиши /help, чтобы посмотреть команды."
            )

    def handle_start(self, chat_id):
        keyboard = {
            "inline_keyboard": [
                [
                    {"text": "➕ Создать команду", "callback_data": "create_team"},
                ],
                [
                    {"text": "🔑 Присоединиться к команде", "callback_data": "join_team"},
                ],
                [
                    {"text": "🔗 Привязать аккаунт сайта", "callback_data": "site_link"},
                ],
                [
                    {"text": "❓ Помощь", "callback_data": "show_start_help"},
                ],
            ]
        }

        self.bot.send_message(
            chat_id,
            "Привет! Это Kanban Bot для командной работы.\n\n"
            "Здесь можно вести задачи проекта по Kanban-доске прямо в Telegram.\n\n"
            "Чтобы начать работу, создай команду или присоединись к существующей по коду.",
            reply_markup=keyboard,
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

    def handle_link(self, chat_id, user_id, username):
        data, error = site_api.request_link_code(user_id, username)
        if error:
            self.bot.send_message(chat_id, error)
            return
        self.bot.send_message(
            chat_id,
            "Привязка к сайту IMCTech Kanban.\n\n"
            f"Твой код: {data['code']}\n"
            f"Действует {data['expires_in_minutes']} мин.\n\n"
            "Зайди на сайт под своим аккаунтом, нажми кнопку «Telegram» "
            "и введи этот код."
        )

    def handle_my_tasks(self, chat_id, user_id):
        tasks = site_api.get_tasks(user_id)
        if tasks is None:
            self.bot.send_message(chat_id, "Сначала привяжи аккаунт командой /link.")
            return
        self.bot.send_message(chat_id, site_api.format_tasks(tasks))

    def handle_my_deadlines(self, chat_id, user_id):
        tasks = site_api.get_deadlines(user_id)
        if tasks is None:
            self.bot.send_message(chat_id, "Сначала привяжи аккаунт командой /link.")
            return
        self.bot.send_message(chat_id, site_api.format_deadlines(tasks))

    def handle_user_state(self, message):
        chat_id = message["chat"]["id"]
        user_id = message["from"]["id"]
        username = message["from"].get("username", "unknown")
        text = message.get("text", "").strip()

        state = self.bot.user_states.get(user_id)

        if state is None:
            return

        action = state.get("action")

        if action == "create_team":
            self.process_create_team(chat_id, user_id, username, text)

        elif action == "join_team":
            self.process_join_team(chat_id, user_id, username, text)

        elif action == "add_task":
            self.process_add_task_step(chat_id, user_id, text)

        else:
            self.bot.send_message(chat_id, "Неизвестное действие.")
            del self.bot.user_states[user_id]

    def process_create_team(self, chat_id, user_id, username, team_name):
        team, error = create_team(user_id, username, team_name)

        if error:
            self.bot.send_message(chat_id, error)
            return

        del self.bot.user_states[user_id]

        keyboard = {
            "inline_keyboard": [
                [
                    {"text": "🏠 Открыть меню", "callback_data": "main_menu"},
                ]
            ]
        }

        self.bot.send_message(
            chat_id,
            "Команда создана!\n\n"
            f"Название: {team['name']}\n"
            f"Код команды: {team['code']}\n\n"
            "Отправь этот код другим участникам, чтобы они могли присоединиться.",
            reply_markup=keyboard,
        )
    
    def process_join_team(self, chat_id, user_id, username, code):
        team, error = join_team(user_id, username, code)

        if error:
            self.bot.send_message(chat_id, error)
            return

        del self.bot.user_states[user_id]

        keyboard = {
            "inline_keyboard": [
                [
                    {"text": "🏠 Открыть меню", "callback_data": "main_menu"},
                ]
            ]
        }

        self.bot.send_message(
            chat_id,
            "Ты присоединился к команде!\n\n"
            f"Название: {team['name']}\n"
            f"Код команды: {team['code']}",
            reply_markup=keyboard,
        )

    def process_add_task_step(self, chat_id, user_id, text):
        state = self.bot.user_states[user_id]
        step = state.get("step")
        data = state.get("data", {})

        if step == "title":
            data["title"] = text
            state["step"] = "description"

            self.bot.send_message(
                chat_id,
                "Теперь введи описание задачи:"
            )

        elif step == "description":
            data["description"] = text
            state["step"] = "assignee"

            self.bot.send_message(
                chat_id,
                "Теперь введи исполнителя задачи:"
            )

        elif step == "assignee":
            data["assignee"] = text
            state["step"] = "deadline"

            self.bot.send_message(
                chat_id,
                "Теперь введи дедлайн задачи.\n\n"
                "Например: 25.05"
            )

        elif step == "deadline":
            data["deadline"] = text
            state["step"] = "priority"

        state["data"] = data
        self.bot.user_states[user_id] = state

        if state["step"] == "priority":
            self.bot.send_message(
                chat_id,
                "Выбери приоритет задачи:",
                reply_markup=task_priority_keyboard(),
            )
