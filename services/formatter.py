PRIORITY_EMOJI = {
    "low": "🟢",
    "medium": "🟡",
    "high": "🔴",
}


def format_task(task):
    priority_label = f"{PRIORITY_EMOJI.get(task['priority'], '')} {task['priority']}"
    lines = [
        f"<b>#{task['task_id']} {task['title']}</b>",
        f"📋 {task['description']}",
        f"👤 Исполнитель: {task['assignee']}",
        f"📌 Статус: {task['status']}",
        f"⚡ Приоритет: {priority_label}",
        f"📅 Дедлайн: {task['deadline']}",
    ]
    if task.get("comments"):
        lines.append(f"💬 Комментариев: {len(task['comments'])}")
    return "\n".join(lines)

def format_board(grouped_tasks):
    lines = ["<b>Kanban доска:</b>\n"]
    for status, tasks in grouped_tasks.items():
        lines.append(f"\n<b>{status}</b> ({len(tasks)})")
        if not tasks:
            lines.append("  — пусто")
        for task in tasks:
            priority_label = PRIORITY_EMOJI.get(task["priority"], "")
            lines.append(f"  #{task['task_id']} {task['title']} {priority_label} 👤 {task['assignee']}")
    return "\n".join(lines)
