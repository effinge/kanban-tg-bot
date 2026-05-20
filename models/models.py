from dataclasses import dataclass


@dataclass
class Task:
    task_id: int
    title: str
    description: str
    assignee: str
    deadline: str
    priority: str = "medium"
    status: str = "backlog"
    created_at: str | None = None

    def to_text(self):
        return (
            f"#{self.task_id} {self.title}\n\n"
            f"Описание: {self.description}\n"
            f"Исполнитель: {self.assignee}\n"
            f"Статус: {self.status}\n"
            f"Приоритет: {self.priority}\n"
            f"Дедлайн: {self.deadline}"
        )