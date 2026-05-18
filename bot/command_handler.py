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
        
        self.bot.send_message(
            chat_id,
            "Главное меню бота.\n\nВыберите раздел.",
            reply_markup=keyboard
        )