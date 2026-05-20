TASK_STATUSES = [
    ("backlog", "Backlog"),
    ("todo", "To Do"),
    ("in_progress", "In Progress"),
    ("review", "Review"),
    ("done", "Done"),
]


def main_menu_keyboard():
    return {
        "inline_keyboard": [
            [
                {"text": "📋 Доска", "callback_data": "show_board"},
                {"text": "📌 Все задачи", "callback_data": "show_tasks"},
            ],
            [
                {"text": "➕ Создать задачу", "callback_data": "task:add_help"},
                {"text": "👥 Участники", "callback_data": "show_members"},
            ],
            [
                {"text": "📊 Статистика", "callback_data": "show_stats"},
                {"text": "⏰ Дедлайны", "callback_data": "show_deadlines"},
            ],
            [
                {"text": "❓ Помощь", "callback_data": "show_help"},
            ],
        ]
    }


def tasks_keyboard(tasks):
    keyboard = []

    for task in tasks:
        keyboard.append(
            [
                {
                    "text": f"#{task.task_id}",
                    "callback_data": f"task:show:{task.task_id}",
                },
                {
                    "text": "➡️ Статус",
                    "callback_data": f"task:move_menu:{task.task_id}",
                },
                {
                    "text": "🗑 Удалить",
                    "callback_data": f"task:delete_confirm:{task.task_id}",
                },
            ]
        )

    keyboard.append(
        [
            {"text": "➕ Создать", "callback_data": "task:add_help"},
            {"text": "📋 Доска", "callback_data": "show_board"},
        ]
    )

    return {"inline_keyboard": keyboard}


def task_actions_keyboard(task_id):
    return {
        "inline_keyboard": [
            [
                {
                    "text": "➡️ Изменить статус",
                    "callback_data": f"task:move_menu:{task_id}",
                },
                {
                    "text": "🗑 Удалить",
                    "callback_data": f"task:delete_confirm:{task_id}",
                },
            ],
            [
                {"text": "📌 Все задачи", "callback_data": "show_tasks"},
                {"text": "📋 Доска", "callback_data": "show_board"},
            ],
        ]
    }


def task_status_keyboard(task_id, current_status=None):
    keyboard = []

    for status, title in TASK_STATUSES:
        text = f"✓ {title}" if status == current_status else title
        keyboard.append(
            [
                {
                    "text": text,
                    "callback_data": f"task:move:{task_id}:{status}",
                }
            ]
        )

    keyboard.append(
        [
            {
                "text": "↩️ Назад к задаче",
                "callback_data": f"task:show:{task_id}",
            }
        ]
    )

    return {"inline_keyboard": keyboard}


def delete_confirm_keyboard(task_id):
    return {
        "inline_keyboard": [
            [
                {
                    "text": "✅ Да, удалить",
                    "callback_data": f"task:delete:{task_id}",
                },
                {
                    "text": "↩️ Отмена",
                    "callback_data": f"task:show:{task_id}",
                },
            ]
        ]
    }


def board_keyboard():
    return {
        "inline_keyboard": [
            [
                {"text": "📌 Все задачи", "callback_data": "show_tasks"},
                {"text": "➕ Создать", "callback_data": "task:add_help"},
            ],
            [
                {"text": "🔄 Обновить доску", "callback_data": "show_board"},
            ],
        ]
    }
