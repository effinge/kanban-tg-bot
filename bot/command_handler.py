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
    
        
        self.bot.send_message(
            chat_id,
            "Главное меню бота.\n\n Выберите раздел.",
            reply_markup=keyboard
        )