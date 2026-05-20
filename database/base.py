import os
import sqlite3
import sys

sys.stdout.reconfigure(encoding='utf-8')

DB_DIR = "database"
DB_NAME = os.path.join(DB_DIR, "dbase.db")


def get_connection():
    os.makedirs(DB_DIR, exist_ok=True)
    return sqlite3.connect(DB_NAME)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        assignee TEXT,
        deadline TEXT,
        priority TEXT,
        status TEXT DEFAULT 'backlog',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (team_id) REFERENCES teams(id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS members (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        telegram_id INTEGER
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS comments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task_id INTEGER NOT NULL,
        author TEXT,
        text TEXT NOT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (task_id) REFERENCES tasks(id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS task_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task_id INTEGER NOT NULL,
        old_status TEXT,
        new_status TEXT,
        changed_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (task_id) REFERENCES tasks(id)
    )
    """)
    
    cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS teams (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        code TEXT NOT NULL UNIQUE,
        owner_user_id INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS team_members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            team_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            username TEXT,
            role TEXT DEFAULT 'member',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (team_id) REFERENCES teams(id)
        )
        """)    

    conn.commit()
    conn.close()

def add_task(title, description, assignee, deadline, priority) -> int:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO tasks (title, description, assignee, deadline, priority)
    VALUES (?, ?, ?, ?, ?)
    """, (title, description, assignee, deadline, priority))

    conn.commit()
    task_id = cursor.lastrowid
    conn.close()

    return task_id

def get_task(task_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    task = cursor.fetchone()

    conn.close()
    return task

def get_all_tasks():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM tasks")
    tasks = cursor.fetchall()

    conn.close()
    return tasks

def get_tasks_by_status(status):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM tasks WHERE status = ?", (status,))
    tasks = cursor.fetchall()

    conn.close()
    return tasks

def update_task_status(task_id, new_status):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT status FROM tasks WHERE id = ?", (task_id,))
    result = cursor.fetchone()

    if result is None:
        conn.close()
        return False

    old_status = result[0]

    cursor.execute("""
    UPDATE tasks
    SET status = ?
    WHERE id = ?
    """, (new_status, task_id))

    cursor.execute("""
    INSERT INTO task_history (task_id, old_status, new_status)
    VALUES (?, ?, ?)
    """, (task_id, old_status, new_status))

    conn.commit()
    conn.close()

    return True

def delete_task(task_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))

    conn.commit()
    deleted = cursor.rowcount
    conn.close()

    return deleted > 0

def add_member(name, telegram_id=None):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO members (name, telegram_id)
    VALUES (?, ?)
    """, (name, telegram_id))

    conn.commit()
    member_id = cursor.lastrowid
    conn.close()

    return member_id

def get_all_members():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM members")
    members = cursor.fetchall()

    conn.close()
    return members

def add_comment(task_id, author, text):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO comments (task_id, author, text)
    VALUES (?, ?, ?)
    """, (task_id, author, text))

    conn.commit()
    comment_id = cursor.lastrowid
    conn.close()

    return comment_id

def get_comments_by_task(task_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT * FROM comments
    WHERE task_id = ?
    ORDER BY created_at
    """, (task_id,))

    comments = cursor.fetchall()

    conn.close()
    return comments

def get_tasks_count_by_status():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT status, COUNT(*)
        FROM tasks
        GROUP BY status
        """
    )

    rows = cursor.fetchall()

    conn.close()

    return dict(rows)

def get_tasks_ordered_by_deadline():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, title, description, assignee, deadline, priority, status, created_at
        FROM tasks
        ORDER BY deadline
        """
    )

    rows = cursor.fetchall()

    conn.close()

    return rows

def get_total_tasks_count():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM tasks
        """
    )

    count = cursor.fetchone()[0]

    conn.close()

    return count

def get_members_count():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM members
        """
    )

    count = cursor.fetchone()[0]

    conn.close()

    return count

def add_team(name, code, owner_user_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO teams (name, code, owner_user_id)
        VALUES (?, ?, ?)
        """,
        (name, code, owner_user_id),
    )

    team_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return team_id


def get_team_by_code(code):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, name, code, owner_user_id
        FROM teams
        WHERE code = ?
        """,
        (code,),
    )

    team = cursor.fetchone()

    conn.close()

    return team


def add_team_member(team_id, user_id, username, role="member"):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id
        FROM team_members
        WHERE team_id = ? AND user_id = ?
        """,
        (team_id, user_id),
    )

    existing_member = cursor.fetchone()

    if existing_member is not None:
        conn.close()
        return False

    cursor.execute(
        """
        INSERT INTO team_members (team_id, user_id, username, role)
        VALUES (?, ?, ?, ?)
        """,
        (team_id, user_id, username, role),
    )

    conn.commit()
    conn.close()

    return True


def get_user_team(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT teams.id, teams.name, teams.code
        FROM teams
        JOIN team_members ON teams.id = team_members.team_id
        WHERE team_members.user_id = ?
        LIMIT 1
        """,
        (user_id,),
    )

    team = cursor.fetchone()

    conn.close()

    return team


def get_team_members(team_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT user_id, username, role
        FROM team_members
        WHERE team_id = ?
        ORDER BY id
        """,
        (team_id,),
    )

    members = cursor.fetchall()

    conn.close()

    return members