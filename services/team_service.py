import random
import string

from database.base import (
    add_team,
    add_team_member,
    get_team_by_code,
    get_user_team,
    get_team_members,
    remove_team_member,
)


def generate_team_code(length=6):
    symbols = string.ascii_uppercase + string.digits
    return "".join(random.choice(symbols) for _ in range(length))


def create_team(user_id, username, team_name):
    if not team_name:
        return None, "Название команды не может быть пустым."

    existing_team = get_user_team(user_id)

    if existing_team is not None:
        return None, "Ты уже состоишь в команде."

    code = generate_team_code()

    while get_team_by_code(code) is not None:
        code = generate_team_code()

    team_id = add_team(
        name=team_name,
        code=code,
        owner_user_id=user_id,
    )

    add_team_member(
        team_id=team_id,
        user_id=user_id,
        username=username,
        role="owner",
    )

    return {
        "id": team_id,
        "name": team_name,
        "code": code,
    }, None


def join_team(user_id, username, code):
    if not code:
        return None, "Код команды не может быть пустым."

    existing_team = get_user_team(user_id)

    if existing_team is not None:
        return None, "Ты уже состоишь в команде."

    code = code.upper()
    team = get_team_by_code(code)

    if team is None:
        return None, "Команда с таким кодом не найдена."

    team_id = team[0]
    team_name = team[1]
    team_code = team[2]

    add_team_member(
        team_id=team_id,
        user_id=user_id,
        username=username,
        role="member",
    )

    return {
        "id": team_id,
        "name": team_name,
        "code": team_code,
    }, None


def user_has_team(user_id):
    return get_user_team(user_id) is not None


def get_user_team_id(user_id):
    team = get_user_team(user_id)

    if team is None:
        return None

    return team[0]


def get_team_members_text(user_id):
    team = get_user_team(user_id)

    if team is None:
        return "Сначала создай команду или присоединись к ней через /start."

    team_id = team[0]
    team_name = team[1]
    team_code = team[2]

    members = get_team_members(team_id)

    if not members:
        return "Участников пока нет."

    result = (
        f"Команда: {team_name}\n"
        f"Код: {team_code}\n\n"
        "Участники:\n"
    )

    for index, member in enumerate(members, start=1):
        username = member[1] or "unknown"
        role = member[2]

        result += f"{index}. @{username} — {role}\n"

    return result


def leave_team(user_id):
    team = get_user_team(user_id)

    if team is None:
        return False, "Ты не состоишь в команде."

    success = remove_team_member(user_id)

    if not success:
        return False, "Не удалось выйти из команды."

    return True, f"Ты вышел из команды «{team[1]}»."
