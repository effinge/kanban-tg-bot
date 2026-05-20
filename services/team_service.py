import random
import string

from database.base import (
    add_team,
    add_team_member,
    get_team_by_code,
    get_user_team,
)


def generate_team_code(length=6):
    symbols = string.ascii_uppercase + string.digits
    return "".join(random.choice(symbols) for _ in range(length))


def create_team(user_id, username, team_name):
    if not team_name:
        return None, "Название команды не может быть пустым."

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

    code = code.upper()
    team = get_team_by_code(code)

    if team is None:
        return None, "Команда с таким кодом не найдена."

    team_id = team[0]
    team_name = team[1]

    add_team_member(
        team_id=team_id,
        user_id=user_id,
        username=username,
        role="member",
    )

    return {
        "id": team_id,
        "name": team_name,
        "code": code,
    }, None


def user_has_team(user_id):
    team = get_user_team(user_id)
    return team is not None