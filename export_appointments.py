import pandas as pd
import sqlite3

conn = sqlite3.connect('database.db')
df = pd.read_sql_query("SELECT * FROM appointments", conn)
df.to_excel("appointments.xlsx", index=False)
conn.close()
print("✅ Appointments exported to appointments.xlsx")
