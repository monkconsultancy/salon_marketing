import sqlite3

staff_names = ["Riya", "Amit", "Sara", "Vikram"]

with sqlite3.connect('database.db') as conn:
    for name in staff_names:
        conn.execute("INSERT INTO staff (name) VALUES (?)", (name,))
    conn.commit()

print("✅ Staff seeded:", ", ".join(staff_names))
