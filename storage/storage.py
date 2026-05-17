import json
import os

STORAGE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "tasks.json")

def _ensure_file() -> None:
    os.makedirs(os.path.dirname(STORAGE_PATH), exist_ok=True)
    if not os.path.exists(STORAGE_PATH):
        with open(STORAGE_PATH, "w", encoding="utf-8") as f:
            json.dump([], f)

def load_tasks() -> list:
    _ensure_file()
    with open(STORAGE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_tasks(tasks: list) -> None:
    _ensure_file()
    with open(STORAGE_PATH, "w", encoding="utf-8") as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)