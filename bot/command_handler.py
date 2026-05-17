from services.task_service import create_task
from services.formatter import format_task

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
    
    def handle_add(self, chat_id: int, text: str) -> None:
        raw = text.removeprefix("/add").strip()
        parts = [p.strip() for p in raw.split("|")]

        if len(parts) != 5:
            self.bot.send_message(
                chat_id,
             "Неверный формат.\n Используй:\n/add Название | Описание | Исполнитель | Дедлайн | Приоритет"
            )
            return

        title, description, assignee, deadline, priority = parts

        if not title:
            self.bot.send_message(chat_id, "Название не может быть пустым.")
            return

        task = create_task(title, description, assignee, deadline, priority)
        self.bot.send_message(chat_id, f"Задача создана.\n\n{format_task(task)}")
        
        self.bot.send_message(
            chat_id,
            "Главное меню бота.\n\n Выберите раздел.",
            reply_markup=keyboard
        )