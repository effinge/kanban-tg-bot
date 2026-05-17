PRIORITY_EMOJI = {
    "low": "🟢",
    "medium": "🟡",
    "high": "🔴",
}

def format_task(task: dict) -> str:
    priority_label = f"{PRIORITY_EMOJI.get(task['priority'], '')} {task['priority']}"
    lines = [
        f"<b>#{task['id']} {task['title']}</b>",
        f"📋 {task['description']}",
        f"👤 Исполнитель: {task['assignee']}",
        f"📌 Статус: {task['status']}",
        f"⚡ Приоритет: {priority_label}",
        f"📅 Дедлайн: {task['deadline']}",
    ]
    if task.get("comments"):
        lines.append(f"💬 Комментариев: {len(task['comments'])}")
    return "\n".join(lines)