import os

import requests
from dotenv import load_dotenv

load_dotenv()

SITE_API_URL = os.getenv("SITE_API_URL", "http://localhost:8000/api")
BOT_API_SECRET = os.getenv("BOT_API_SECRET", "dev-bot-secret")
HEADERS = {"X-Bot-Secret": BOT_API_SECRET}

STATUS_LABELS = {
    "backlog": "Бэклог",
    "todo": "Нужно сделать",
    "in_progress": "В процессе",
    "review": "На проверке",
    "done": "Выполнено",
}
PRIORITY_LABELS = {"low": "низкий", "medium": "средний", "high": "высокий"}


def request_link_code(telegram_id, username):
    try:
        response = requests.post(
            f"{SITE_API_URL}/telegram/request-code",
            json={"telegram_id": telegram_id, "username": username},
            headers=HEADERS,
            timeout=10,
        )
        response.raise_for_status()
        return response.json(), None
    except requests.RequestException:
        return None, "Сайт сейчас недоступен. Попробуй позже."


def _get_list(path, telegram_id):
    try:
        response = requests.get(
            f"{SITE_API_URL}/telegram/{telegram_id}/{path}",
            headers=HEADERS,
            timeout=10,
        )
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        return None


def get_tasks(telegram_id):
    return _get_list("tasks", telegram_id)


def get_deadlines(telegram_id):
    return _get_list("deadlines", telegram_id)


def fetch_notifications():
    try:
        response = requests.get(
            f"{SITE_API_URL}/telegram/notifications/pending",
            headers=HEADERS,
            timeout=10,
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        return []


def ack_notifications(ids):
    if not ids:
        return
    try:
        requests.post(
            f"{SITE_API_URL}/telegram/notifications/ack",
            json={"ids": ids},
            headers=HEADERS,
            timeout=10,
        )
    except requests.RequestException:
        pass


def format_tasks(tasks):
    if not tasks:
        return "На сайте у тебя пока нет задач."

    lines = ["Твои задачи с сайта:\n"]
    for task in tasks:
        lines.append(
            f"#{task['id']} {task['title']}\n"
            f"Проект: {task.get('project_name') or '—'}\n"
            f"Статус: {STATUS_LABELS.get(task['status'], task['status'])}\n"
            f"Дедлайн: {task['deadline']}\n"
            f"Приоритет: {PRIORITY_LABELS.get(task['priority'], task['priority'])}\n"
        )
    return "\n".join(lines)


def format_deadlines(tasks):
    if not tasks:
        return "Открытых задач с дедлайнами нет."

    lines = ["Ближайшие дедлайны:\n"]
    for task in tasks:
        status = STATUS_LABELS.get(task["status"], task["status"])
        lines.append(f"• {task['deadline']} — {task['title']} ({status})")
    return "\n".join(lines)
