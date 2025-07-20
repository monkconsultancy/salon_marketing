from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import datetime

app = Flask(__name__)




# DB Initialization
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY,
            name TEXT,
            service TEXT,
            rating INTEGER,
            comments TEXT,
            date TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS referrals (
            id INTEGER PRIMARY KEY,
            referrer_name TEXT,
            referred_name TEXT,
            status TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Routes
@app.route('/')
def home():
    return render_template("index.html")

@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if request.method == 'POST':
        name = request.form['name']
        service = request.form['service']
        rating = request.form['rating']
        comments = request.form['comments']
        date = datetime.now().strftime("%Y-%m-%d")

        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("INSERT INTO feedback (name, service, rating, comments, date) VALUES (?, ?, ?, ?, ?)",
                  (name, service, rating, comments, date))
        conn.commit()
        conn.close()
        return redirect('/')
    return render_template("feedback.html")

@app.route('/referral', methods=['GET', 'POST'])
def referral():
    if request.method == 'POST':
        referrer = request.form['referrer']
        referred = request.form['referred']
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("INSERT INTO referrals (referrer_name, referred_name, status) VALUES (?, ?, ?)",
                  (referrer, referred, "Pending"))
        conn.commit()
        conn.close()
        return redirect('/')
    return render_template("referral.html")



import sqlite3
import pandas as pd

def export_feedback_to_excel():
    conn = sqlite3.connect('database.db')
    df = pd.read_sql_query("SELECT * FROM feedback", conn)
    df.to_excel("feedback_data.xlsx", index=False)
    conn.close()
    print("✅ Feedback data exported to feedback_data.xlsx")

def export_referral_to_excel():
    conn = sqlite3.connect('database.db')
    df = pd.read_sql_query("SELECT * FROM referrals", conn)
    df.to_excel("referral_data.xlsx", index=False)
    conn.close()
    print("✅ Referral data exported to referral_data.xlsx")

# Run both exports
export_feedback_to_excel()
export_referral_to_excel()



if __name__ == '__main__':
    app.run(debug=True)
