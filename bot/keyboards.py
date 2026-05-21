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
                {"text": "➕ Создать задачу", "callback_data": "add_task"},
            ],
            [
                {"text": "🧱 Доска", "callback_data": "show_board"},
                {"text": "📋 Все задачи", "callback_data": "show_tasks"},
            ],
            [
                {"text": "👥 Участники", "callback_data": "show_members"},
                {"text": "📊 Статистика", "callback_data": "show_stats"},
            ],
            [
                {"text": "⏰ Дедлайны", "callback_data": "show_deadlines"},
                {"text": "❓ Помощь", "callback_data": "show_help"},
            ],
            [
                {"text": "🚪 Выйти из команды", "callback_data": "leave_team_confirm"},
            ],
        ]
    }


def team_members_keyboard():
    return {
        "inline_keyboard": [
            [
                {"text": "🚪 Выйти из команды", "callback_data": "leave_team_confirm"},
            ],
            [
                {"text": "🏠 Главное меню", "callback_data": "main_menu"},
            ],
        ]
    }


def leave_team_confirm_keyboard():
    return {
        "inline_keyboard": [
            [
                {"text": "✅ Да, выйти", "callback_data": "leave_team"},
                {"text": "↩️ Отмена", "callback_data": "show_members"},
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
            {"text": "➕ Создать", "callback_data": "add_task"},
            {"text": "🧱 Доска", "callback_data": "show_board"},
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
                {"text": "📋 Все задачи", "callback_data": "show_tasks"},
                {"text": "🧱 Доска", "callback_data": "show_board"},
            ],
            [
                {"text": "➕ Создать задачу", "callback_data": "add_task"},
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
                {"text": "📋 Все задачи", "callback_data": "show_tasks"},
                {"text": "➕ Создать", "callback_data": "add_task"},
            ],
            [
                {"text": "🔄 Обновить доску", "callback_data": "show_board"},
            ],
            [
                {"text": "🏠 Главное меню", "callback_data": "main_menu"},
            ],
        ]
    }


def task_priority_keyboard():
    return {
        "inline_keyboard": [
            [
                {"text": "Low", "callback_data": "priority_low"},
                {"text": "Medium", "callback_data": "priority_medium"},
            ],
            [
                {"text": "High", "callback_data": "priority_high"},
                {"text": "Critical", "callback_data": "priority_critical"},
            ],
        ]
    }


def after_task_created_keyboard():
    return {
        "inline_keyboard": [
            [
                {"text": "🧱 Открыть доску", "callback_data": "show_board"},
                {"text": "📋 Все задачи", "callback_data": "show_tasks"},
            ],
            [
                {"text": "➕ Создать ещё задачу", "callback_data": "add_task"},
            ],
            [
                {"text": "🏠 Главное меню", "callback_data": "main_menu"},
            ],
        ]
    }
