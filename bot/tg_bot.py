import os
import time

import requests
from dotenv import load_dotenv

from bot.command_handler import CommandHandler
from bot.callback_handler import CallbackHandler
from services import site_api

NOTIFY_INTERVAL_SECONDS = 30


class TelegramBot:
    def __init__(self):
        load_dotenv()

        self.token = os.getenv("BOT_TOKEN")
        self.api_url = f"https://api.telegram.org/bot{self.token}"
        self.last_update_id = 0
        self.last_notify_check = 0

        self.user_states = {}

        self.command_handler = CommandHandler(self)
        self.callback_handler = CallbackHandler(self)

    def get_updates(self):
        url = f"{self.api_url}/getUpdates"

        params = {
            "offset": self.last_update_id + 1,
            "timeout": 30,
        }

        response = requests.get(url, params=params)
        data = response.json()

        if not data.get("ok"):
            return []

        return data.get("result", [])

    def send_message(self, chat_id, text, reply_markup=None):
        url = f"{self.api_url}/sendMessage"

        payload = {
            "chat_id": chat_id,
            "text": text,
        }

        if reply_markup is not None:
            payload["reply_markup"] = reply_markup

        requests.post(url, json=payload)

    def answer_callback_query(self, callback_query_id, text=None):
        url = f"{self.api_url}/answerCallbackQuery"

        payload = {
            "callback_query_id": callback_query_id,
        }

        if text is not None:
            payload["text"] = text

        requests.post(url, json=payload)

    def run(self):
        print("Bot started")

        while True:
            updates = self.get_updates()

            for update in updates:
                self.last_update_id = update["update_id"]

                if "message" in update:
                    self.command_handler.handle(update["message"])

                elif "callback_query" in update:
                    self.callback_handler.handle(update["callback_query"])

            self.deliver_notifications()
            time.sleep(1)

    def deliver_notifications(self):
        now = time.time()
        if now - self.last_notify_check < NOTIFY_INTERVAL_SECONDS:
            return
        self.last_notify_check = now

        items = site_api.fetch_notifications()
        delivered = []
        for item in items:
            self.send_message(item["telegram_id"], item["text"])
            delivered.append(item["id"])

        if delivered:
            site_api.ack_notifications(delivered)
