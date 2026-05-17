class CallbackHandler:
    def __init__(self, bot):
        self.bot = bot

    def handle(self, callback_query):
        chat_id = callback_query["message"]["chat"]["id"]
        callback_data = callback_query["data"]

        if callback_data == "show_board":
            self.bot.send_message(chat_id, "Раздел «Доска» пока в разработке.")

        elif callback_data == "show_members":
            self.bot.send_message(chat_id, "Раздел «Участники» пока в разработке.")

        elif callback_data == "show_stats":
            self.bot.send_message(chat_id, "Раздел «Статистика» пока в разработке.")

        elif callback_data == "show_deadlines":
            self.bot.send_message(chat_id, "Раздел «Дедлайны» пока в разработке.")

        elif callback_data == "show_help":
            self.bot.send_message(
                chat_id,
                "Помощь:\n\n"
                "/start — запуск бота\n"
                "/help — помощь\n"
                "/menu — главное меню"
            )

        else:
            self.bot.send_message(chat_id, "Неизвестное действие.")