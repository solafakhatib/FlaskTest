import sqlite3

conn = sqlite3.connect('instance/tasks.db')
cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE subtask (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        content TEXT NOT NULL,
        is_done BOOLEAN DEFAULT 0,
        task_id INTEGER NOT NULL,
        FOREIGN KEY(task_id) REFERENCES task(id) ON DELETE CASCADE
    );
""")

conn.commit()
conn.close()