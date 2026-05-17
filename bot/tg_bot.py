import os
import requests
import time
from dotenv import load_dotenv

from bot.command_handler import CommandHandler
from bot.callback_handler import CallbackHandler
class TelegramBot:
    def __init__(self):
        load_dotenv()
        
        self.token = os.getenv("BOT_TOKEN")
        self.api_url = f"https://api.telegram.org/bot{self.token}"
        self.last_update_id = 0

        self.command_handler = CommandHandler(self)
        self.callback_handler = CallbackHandler(self)
    
    def get_updates(self):
        url = f"{self.api_url}/getUpdates"
        
        params = {
            "offset": self.last_update_id + 1,
            "timeout": 30
        }
        
        response = requests.get(url, params=params)
        data = response.json()
        
        if not data.get("ok"):
            return []
        
        return data.get("result",[])
    
    def send_message(self, chat_id, text, reply_markup=None):
        url = f"{self.api_url}/sendMessage"

        payload = {
            "chat_id": chat_id,
            "text": text
        }

        if reply_markup is not None:
            payload["reply_markup"] = reply_markup

        response = requests.post(url, json=payload)

        print("SEND MESSAGE RESPONSE:", response.json())
        
        
    # def run(self):
        # print("start")
        
        # while True:
        #     print("check updates")
        #     updates = self.get_updates()
            
        #     for update in updates:
        #         self.last_update_id = update["update_id"]
                
        #         if "message" in update:
        #             self.command_handler.handle(update["message"])
                
        #         elif "callback_query" in update:
        #             self.callback_handler.handle(update["callback_query"])
            
        #     time.sleep(1)
    
    def run(self):
        print("Bot started")

        while True:
            print("check updates")

            updates = self.get_updates()
            print("updates:", updates)

            for update in updates:
                self.last_update_id = update["update_id"]

                if "message" in update:
                    print("message found")
                    print(update["message"])
                    self.command_handler.handle(update["message"])

                elif "callback_query" in update:
                    print("callback found")
                    print(update["callback_query"])
                    self.callback_handler.handle(update["callback_query"])

            time.sleep(1)