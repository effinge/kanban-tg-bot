import sqlite3
import sys

sys.stdout.reconfigure(encoding='utf-8')

DB_NAME = 'database/dbase.db'

def get_connection():
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
        status TEXT DEFAULT 'new',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
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

    conn.commit()
    conn.close()

def add_task(title, description, assignee, deadline, priority):
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

print(get_all_tasks())
print(get_task(2))