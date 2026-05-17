VALID_PRIORITIES = {"low", "medium", "high"}
DEFAULT_STATUS = "Backlog"

def make_task(id: int, title: str, description: str, assignee: str, deadline: str, priority: str) -> dict:
    priority = priority.lower()
    if priority not in VALID_PRIORITIES:
        priority = "medium"

    return {
        "id": id,
        "title": title,
        "description": description,
        "assignee": assignee,
        "deadline": deadline,
        "priority": priority,
        "status": DEFAULT_STATUS,
        "comments": [],
    }