from bot.tg_bot import TelegramBot
from database.base import init_db

def main():
    init_db()
    bot = TelegramBot()
    bot.run()
    
if __name__ == "__main__":
    main()
