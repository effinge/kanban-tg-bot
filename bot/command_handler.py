from services.task_service import create_task, validate_task
from models.models import Task
class CommandHandler:
    def __init__(self, bot):
        self.bot = bot
        
    def handle(self, message):
        chat_id = message["chat"]["id"]
        text = message.get("text", "")
        
        if text == "/start":
            self.handle_start(chat_id)
            
        elif text == "/help":
            self.handle_help(chat_id)
            
        elif text == "/menu":
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

        else:
            self.bot.send_message(
            chat_id,
            "Пока такой команды нет. :()"
            )
        
    def handle_start(self, chat_id):
        self.bot.send_message(
            chat_id,
            "Привет! Я Kanban Fefu Bot."
            "Я помогу вашей команде вести задачи по Канбан-доске."
            "Просто напиши /help, чтобы посмотреть команды."
        )
    
    def handle_help(self, chat_id):
        self.bot.send_message(
            chat_id,
            "Основные команды:"
            "Пока нет :()"
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
            "   /add Сделать README | Описать запуск проекта | Иван | 20.05 | high"
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
            priority=priority
        )
        
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
    
    def handle_menu(self, chat_id):
        keyboard = {
            "inline_keyboard": [
                [
                    {"text": "📋 Доска", "callback_data": "show_board"},
                    {"text": "👥 Участники", "callback_data": "show_members"}
                ],
                [
                    {"text": "📊 Статистика", "callback_data": "show_stats"},
                    {"text": "⏰ Дедлайны", "callback_data": "show_deadlines"}
                ],
                [
                    {"text": "❓ Помощь", "callback_data": "show_help"}
                ]
            ]
        }
    def handle_tasks(self, chat_id):
        from services.task_service import get_all_tasks_list
        from services.formatter import format_task_list
        tasks = get_all_tasks_list()
        self.bot.send_message(chat_id, format_task_list(tasks))

    def handle_task(self, chat_id, text):
        from services.task_service import get_task_by_id
        from services.formatter import format_task
        raw = text.removeprefix("/task").strip()
        if not raw.isdigit():
            self.bot.send_message(chat_id, "Укажи номер. Например: /task 1")
            return
        task = get_task_by_id(int(raw))
        if not task:
            self.bot.send_message(chat_id, f"Задача #{raw} не найдена.")
            return
        self.bot.send_message(chat_id, format_task(task))
    
    def handle_board(self, chat_id):
        from services.task_service import get_tasks_by_status_grouped
        from services.formatter import format_board
        grouped = get_tasks_by_status_grouped()
        self.bot.send_message(chat_id, format_board(grouped))
        
    def handle_move(self, chat_id, text):
        from services.task_service import move_task
        raw = text.removeprefix("/move").strip()
        parts = raw.split()

        if len(parts) != 2:
            self.bot.send_message(
                chat_id,
                "Неверный формат.\nИспользуй:\n/move 1 In Progress"
            )
            return

        task_id, new_status = parts[0], " ".join(parts[1:])

        if not task_id.isdigit():
            self.bot.send_message(chat_id, "Укажи номер задачи. Например: /move 1 Done")
            return

        success, error = move_task(int(task_id), new_status)
        if not success:
            self.bot.send_message(chat_id, error)
            return

        self.bot.send_message(chat_id, f"Задача #{task_id} перемещена в {new_status}.")
        
        self.bot.send_message(
            chat_id,
            "Главное меню бота.\n\n Выберите раздел.",
            reply_markup=keyboard
        )