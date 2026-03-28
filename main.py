import sqlite3

conn = sqlite3.connect("forwards.db")
cursor = conn.cursor()

# список таблиц
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
print("Таблицы:", cursor.fetchall())

# данные из таблицы (пример)
cursor.execute("SELECT * FROM forward_counts")
print("Данные:", cursor.fetchall(), "\n")

conn.close()