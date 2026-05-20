from database.base import add_member, get_all_members


def create_member(name):
    if not name:
        return False, "Имя участника не может быть пустым."

    add_member(name)

    return True, None


def get_members_text():
    members = get_all_members()

    if not members:
        return "Участников пока нет."

    result = "Участники команды:\n\n"

    for member_id, name in members:
        result += f"{member_id}. {name}\n"

    return result