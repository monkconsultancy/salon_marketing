from flask import Flask, render_template, request, redirect, send_file
import sqlite3, pandas as pd, os
from datetime import datetime
from twilio.rest import Client

import os
twilio_sid = os.getenv("TWILIO_ACCOUNT_SID")

# login feature 
from werkzeug.security import generate_password_hash, check_password_hash

from flask import Flask, render_template, request, redirect, url_for, session, flash

import sqlite3, pandas as pd, os
from datetime import datetime
from twilio.rest import Client

app = Flask(__name__)


app.secret_key = 'x7f@ks#2Lp90!rA$'  # Use any random long string



# app = Flask(__name__)
DB = 'database.db'



# live update 

def get_current_token():
    today = datetime.now().strftime('%Y-%m-%d')
    with sqlite3.connect(DB) as conn:
        row = conn.execute("SELECT current_token FROM token_status WHERE date=?", (today,)).fetchone()
        return row[0] if row else 0

def set_current_token(new_val):
    today = datetime.now().strftime('%Y-%m-%d')
    with sqlite3.connect(DB) as conn:
        conn.execute(
            "INSERT OR REPLACE INTO token_status (date, current_token) VALUES (?, ?)",
            (today, new_val)
        )



def init_db():
    with sqlite3.connect(DB) as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT, mobile TEXT, service TEXT,
            date TEXT, time TEXT, created_at TEXT,
            staff_id INTEGER
        )''')
        conn.execute('''CREATE TABLE IF NOT EXISTS token_status (
            date TEXT PRIMARY KEY,
            current_token INTEGER DEFAULT 0
        )''')
        # ensure today’s row exists
        today = datetime.now().strftime('%Y-%m-%d')
        conn.execute('INSERT OR IGNORE INTO token_status (date, current_token) VALUES (?,0)', (today,))

        # Add this try-except to ensure queue_number column exists
        try:
            conn.execute("ALTER TABLE appointments ADD COLUMN queue_number INTEGER")
        except sqlite3.OperationalError:
            pass  # Already added, so ignore error

        # You can also add other optional columns here, like:
        # amount_paid, source, address if needed



# ---------- DB INIT ----------
def init_db():
    with sqlite3.connect(DB) as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT, mobile TEXT, service TEXT,
            date TEXT, time TEXT, created_at TEXT,
            staff_id INTEGER
        )''')

        conn.execute('''CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT, rating INTEGER,
            comments TEXT, date TEXT
        )''')

        conn.execute('''CREATE TABLE IF NOT EXISTS staff (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            is_available INTEGER DEFAULT 1
        )''')

init_db()

# login init function

def init_db():
    with sqlite3.connect(DB) as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT, mobile TEXT, service TEXT,
            date TEXT, time TEXT, created_at TEXT,
            staff_id INTEGER,
            address TEXT,
            source TEXT,
            amount_paid REAL
        )''')

        conn.execute('''CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT, rating INTEGER,
            comments TEXT, date TEXT
        )''')

        conn.execute('''CREATE TABLE IF NOT EXISTS staff (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            is_available INTEGER DEFAULT 1
        )''')

        conn.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )''')




# login logout

from functools import wraps

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get("user_id"):
            return redirect(url_for("login", next=request.path))
        return f(*args, **kwargs)
    return wrapper


# login and logout route




@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = sqlite3.connect('database.db')
        user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        conn.close()

        if user and check_password_hash(user[2], password):
            session['user_id'] = user[0]
            return redirect('/admin/dashboard')  # or wherever your admin page is
        else:
            flash("Invalid credentials", "error")
            return redirect('/login')
    
    return render_template('login.html')

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))



# live update feature 




@app.route('/admin/update_token', methods=['POST'])
# @login_required
def update_token():
    new_token = int(request.form['new_token'])
    today = datetime.now().strftime('%Y-%m-%d')
    new_val = int(request.form['new_token'])
    set_current_token(new_val)
    with sqlite3.connect(DB) as conn:
        conn.execute('INSERT OR REPLACE INTO token_status (date, current_token) VALUES (?, ?)', (today, new_token))

    return redirect('/admin/appointments')



  

# appoinemnt counet daily 

def update_db_for_client_tracking():
    with sqlite3.connect(DB) as conn:
        conn.execute("ALTER TABLE appointments ADD COLUMN address TEXT")
        conn.execute("ALTER TABLE appointments ADD COLUMN source TEXT")  # 'Online' or 'Offline'




# ---------- Twilio WhatsApp ----------
TWILIO_ACCOUNT_SID = 'AC559023cc3d36c7a8daf72a0811dcf0da'
TWILIO_AUTH_TOKEN  = '892dbd9d846a76d15bfb4e8f6261167f'
FROM_WA_NUMBER     = 'whatsapp:+17754367476'

twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

def send_whatsapp_message(to_number, body):
    try:
        msg = twilio_client.messages.create(
            body=body,
            from_=FROM_WA_NUMBER,
            to=f'whatsapp:+91{to_number}'
        )
        print("✅ WhatsApp SID:", msg.sid)
    except Exception as e:
        print("❌ WhatsApp error:", e)


# ---------- CUSTOMER BOOK ----------
# @app.route('/book', methods=['GET', 'POST'])
# def book_appointment():
#     with sqlite3.connect(DB) as conn:
#         staff_list = conn.execute("SELECT id, name FROM staff WHERE is_available=1").fetchall()

#     if request.method == 'POST':
#         # Step 1: get next queue number
#         current_token = get_current_token()
#         next_token = current_token + 1
#         set_current_token(next_token)

#         # Step 2: collect form data
#         data = (
#             request.form['name'],
#             request.form['mobile'],
#             request.form['service'],
#             request.form['date'],
#             request.form['time'],
#             datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
#             request.form['staff_id'],
#             request.form['address'],
#             request.form['source'],
#             request.form['amount_paid'],
#             request.form['email'],
#             next_token  # ➕ this is the new queue/token number
#         )

#         # Step 3: insert appointment into DB
#         with sqlite3.connect(DB) as conn:
#             conn.execute("""INSERT INTO appointments
#                 (name, mobile, service, date, time, created_at, staff_id, address, source, amount_paid, email, queue_number)
#                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", data)

#         # Step 4: Show thank you page with token
#         return render_template('thank_you_with_feedback.html', token=next_token)

#     # If GET, show booking form
#     current_token = get_current_token()
#     return render_template('book_appointment.html', staff_list=staff_list, current_token=current_token)


#     return render_template('book_appointment.html', staff_list=staff_list)



@app.route('/book', methods=['GET', 'POST'])
def book_appointment():
    with sqlite3.connect(DB) as conn:
        staff_list = conn.execute("SELECT id, name FROM staff WHERE is_available=1").fetchall()

    if request.method == 'POST':
        current_token = get_current_token()
        next_token = current_token + 1
        set_current_token(next_token)

        name = request.form['name']
        mobile = request.form['mobile']
        service = request.form['service']
        date = request.form['date']
        time = request.form['time']
        staff_id = request.form['staff_id']
        address = request.form['address']
        source = request.form['source']
        amount_paid = request.form['amount_paid']
        email = request.form['email']  # ✅ added email field

        data = (
            name, mobile, service, date, time,
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            staff_id, address, source, amount_paid, email, next_token
        )

        with sqlite3.connect(DB) as conn:
            conn.execute("""INSERT INTO appointments
                (name, mobile, service, date, time, created_at, staff_id, address, source, amount_paid, email, queue_number)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", data)

        return render_template('thank_you_with_feedback.html', token=next_token)

    current_token = get_current_token()
    return render_template('book_only.html', staff_list=staff_list, current_token=current_token)




# / randing feature

@app.route('/')
def home():
    token = get_current_token()
    return render_template('home.html', current_token=token)




# appoinemt count route


@app.route('/admin/clients/today', methods=['GET', 'POST'])
def today_clients():
    selected_date = request.form.get("date") if request.method == "POST" else datetime.now().strftime('%Y-%m-%d')

    if request.method == 'POST':
        # Insert manually added client
        name = request.form['name']
        mobile = request.form['mobile']
        address = request.form['address']
        service = request.form['service']
        source = request.form['source']
        date = request.form['date']
        amount_paid = float(request.form.get('amount_paid') or 0)

        with sqlite3.connect(DB) as conn:
            conn.execute("""
                INSERT INTO appointments (name, mobile, address, service, source, date, amount_paid)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (name, mobile, address, service, source, date, amount_paid))

    with sqlite3.connect(DB) as conn:
        rows = conn.execute("""
            SELECT name, mobile, address, service, source, amount_paid
            FROM appointments
            WHERE date LIKE ?
            ORDER BY time
        """, (selected_date + '%',)).fetchall()

    total_revenue = sum(row[5] or 0 for row in rows)
    total_clients = len(rows)

    return render_template('today_clients.html',
                           clients=rows,
                           today=selected_date,
                           total_revenue=total_revenue,
                           total_clients=total_clients)



# @app.route('/admin/clients/today', methods=['GET', 'POST'])
# def today_clients():
#     today = datetime.now().strftime('%Y-%m-%d')

#     if request.method == 'POST':
#         name = request.form['name']
#         mobile = request.form['mobile']
#         address = request.form['address']
#         service = request.form['service']
#         source = request.form['source']
#         date = request.form['date']
#         # amount_paid=request.form['amount_paid']
        
#         created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

#         # Insert the new client manually (no staff, time, or token needed)
#         with sqlite3.connect(DB) as conn:
#             conn.execute('''
#                 INSERT INTO appointments
#                 (name, mobile, service, date, time, created_at, address, source )
#                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
#             ''', (name, mobile, service, date, "", created_at, address, source, None))

#     # Always fetch updated data
#     with sqlite3.connect(DB) as conn:
#         rows = conn.execute("""
#             SELECT name, mobile, address, service, source, amount_paid
#             FROM appointments
#             WHERE date LIKE ?
#             ORDER BY time
#         """, (today + '%',)).fetchall()

#         total_revenue = sum(r[5] for r in rows if r[5])  # r[5] = amount_paid

#     return render_template('today_clients.html', clients=rows, today=today, total_revenue=total_revenue)


# @app.route('/admin/clients/today', methods=['GET', 'POST'])
# def today_clients():
#     today = datetime.now().strftime('%Y-%m-%d')
#     with sqlite3.connect(DB) as conn:
#         rows = conn.execute("""
#             SELECT name, mobile, address, service, source, amount_paid
#             FROM appointments
#             WHERE date LIKE ?
#             ORDER BY time
#         """, (today + '%',)).fetchall()

#         total_revenue = sum(r[5] for r in rows if r[5])  # r[5] = amount_paid

#     return render_template('today_clients.html', clients=rows, today=today, total_revenue=total_revenue)



# AI flyer generater












# email feature smtp 
from flask_mail import Mail, Message

# Flask-Mail configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'shivamsingh.zak@gmail.com'          # your Gmail ID
app.config['MAIL_PASSWORD'] = 'hrog synb pdpr rryq'     # from Step 2
app.config['MAIL_DEFAULT_SENDER'] = 'shivamsingh.zak@gmail.com'

mail = Mail(app)


def send_email_notification(to_email, subject, body):
    try:
        msg = Message(subject, recipients=[to_email], body=body)
        mail.send(msg)
        print("✅ Email sent to:", to_email)
    except Exception as e:
        print("❌ Email error:", e)





@app.route('/admin/token', methods=['GET','POST'])
@login_required
def manage_token():
    if request.method == 'POST':
        new_val = int(request.form['new_val'])
        set_current_token(new_val)
        return redirect('/admin/token')
    current = get_current_token()
    return render_template('admin_token.html', current=current)


@app.route('/current_token')
def current_token_api():
    return str(get_current_token())



# ---------- ADMIN ----------
@app.route('/admin/appointments')
# @login_required
def view_appointments():
    
    search = request.args.get('search', '')
    date_fr = request.args.get('from', '')
    date_to = request.args.get('to', '')
    current_token = get_current_token()

    q = """SELECT a.*, s.name AS staff_name FROM appointments a 
           LEFT JOIN staff s ON a.staff_id = s.id WHERE 1=1"""
    p = []
    if search:
        q += " AND (a.name LIKE ? OR a.mobile LIKE ? OR a.service LIKE ?)"
        p += [f'%{search}%']*3
    if date_fr:
        q += " AND a.date >= ?"
        p.append(date_fr)
    if date_to:
        q += " AND a.date <= ?"
        p.append(date_to)
    q += " ORDER BY a.date DESC, a.time DESC"

    with sqlite3.connect(DB) as conn:
        appointments = conn.execute(q, p).fetchall()
    # return render_template('admin_appointments.html',
    #                        appointments=appointments,
    #                        search=search, date_from=date_fr, date_to=date_to)
        return render_template('admin_appointments.html',
                           appointments=appointments,
                           search=search, date_from=date_fr, date_to=date_to,
                           current_token=current_token)



@app.route('/admin/export')
def export_appointments():
    with sqlite3.connect(DB) as conn:
        df = pd.read_sql_query("SELECT * FROM appointments", conn)
    file = 'appointments_export.xlsx'
    df.to_excel(file, index=False)
    return send_file(file, as_attachment=True)


@app.route('/admin/delete/<int:id>')
def delete_appointment(id):
    with sqlite3.connect(DB) as conn:
        conn.execute('DELETE FROM appointments WHERE id=?', (id,))
    return redirect('/admin/appointments')


@app.route('/admin/edit/<int:id>', methods=['GET', 'POST'])
def edit_appointment(id):
    with sqlite3.connect(DB) as conn:
        staff_list = conn.execute("SELECT id, name FROM staff").fetchall()

        if request.method == 'POST':
            name = request.form.get('name')
            mobile = request.form.get('mobile')
            service = request.form.get('service')
            date = request.form.get('date')
            time = request.form.get('time')
            staff_id = request.form.get('staff_id')

            conn.execute("""
                UPDATE appointments
                SET name=?, mobile=?, service=?, date=?, time=?, staff_id=?
                WHERE id=?
            """, (name, mobile, service, date, time, staff_id, id))

            return redirect('/admin/appointments')

        appointment = conn.execute('SELECT * FROM appointments WHERE id=?', (id,)).fetchone()

    return render_template('edit_appointment.html', appointment=appointment, staff_list=staff_list)


# notofcation conformation
@app.route('/admin/confirm/<int:id>')
def confirm_appointment(id):
    with sqlite3.connect(DB) as conn:
        row = conn.execute("SELECT name, mobile, service, date, time, email FROM appointments WHERE id=?", (id,)).fetchone()

    if row:
        name, mobile, service, date, time, email = row
        message = f"Hello {name}, your appointment for '{service}' on {date} at {time} is confirmed. Thank you!"

        send_whatsapp_message(mobile, message)
        send_email_notification(email, "Appointment Confirmed", message)  # 👈 Real email now!

    return redirect('/admin/appointments')




@app.route('/admin/reject/<int:id>')
def reject_appointment(id):
    with sqlite3.connect(DB) as conn:
        row = conn.execute("SELECT name, mobile, service, date, time FROM appointments WHERE id=?", (id,)).fetchone()

    if row:
        name, mobile, service, date, time = row
        message = f"Dear {name}, we're sorry but your appointment for '{service}' on {date} at {time} has been rejected due to no available slots."

        # ✅ Send WhatsApp rejection message
        send_whatsapp_message(mobile, message)

        # ✅ Send Email rejection message
        email = f"{mobile}@mailinator.com"  # Optional: replace with real client email if available
        send_email_notification(email, "Appointment Rejected", message)

    return redirect('/admin/appointments')



# ---------- FEEDBACK ----------
@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if request.method == 'POST':
        name = request.form['name']
        rating = request.form['rating']
        comments = request.form['comments']
        date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        with sqlite3.connect(DB) as conn:
            conn.execute('INSERT INTO feedback (name, rating, comments, date) VALUES (?, ?, ?, ?)',
                         (name, rating, comments, date))
        return render_template('thank_you.html')

    return render_template('feedback.html')


@app.route('/admin/feedback')
def admin_feedback():
    with sqlite3.connect(DB) as conn:
        feedbacks = conn.execute("SELECT * FROM feedback ORDER BY date DESC").fetchall()
    return render_template('admin_feedback.html', feedbacks=feedbacks)


@app.route('/admin/feedback/export')
def export_feedback():
    with sqlite3.connect(DB) as conn:
        df = pd.read_sql_query("SELECT * FROM feedback ORDER BY date DESC", conn)
    filename = 'feedback_export.xlsx'
    df.to_excel(filename, index=False)
    return send_file(filename, as_attachment=True)


# ---------- STAFF MANAGEMENT ----------
# @app.route('/admin/staff/schedule')
# def staff_schedule():
#     with sqlite3.connect(DB) as conn:
#         schedule = conn.execute('''
#             SELECT s.name, a.date, a.time, a.service, a.name
#             FROM appointments a
#             JOIN staff s ON a.staff_id = s.id
#             ORDER BY s.name, a.date, a.time
#         ''').fetchall()
#     return render_template('staff_schedule.html', schedule=schedule)

@app.route('/admin/staff/schedule')
def staff_schedule():
    with sqlite3.connect(DB) as conn:
        schedule = conn.execute('''
            SELECT s.name, a.date, a.time, a.service, a.name, a.id, s.id
            FROM appointments a
            JOIN staff s ON a.staff_id = s.id
            ORDER BY s.name, a.date, a.time
        ''').fetchall()

        all_staff = conn.execute("SELECT id, name FROM staff").fetchall()

    return render_template('staff_schedule.html', schedule=schedule, all_staff=all_staff)


@app.route('/admin/staff/update/<int:appointment_id>', methods=['POST'])
def update_staff_assignment(appointment_id):
    new_staff_id = request.form['staff_id']
    with sqlite3.connect(DB) as conn:
        conn.execute("UPDATE appointments SET staff_id = ? WHERE id = ?", (new_staff_id, appointment_id))
    return redirect('/admin/staff/schedule')



@app.route('/admin/staff/add', methods=['GET', 'POST'])
def add_staff():
    if request.method == 'POST':
        name = request.form['name']
        with sqlite3.connect(DB) as conn:
            conn.execute("INSERT INTO staff (name) VALUES (?)", (name,))
        return redirect('/admin/staff/add')
    return '''
        <form method="post" style="margin:40px">
            <input name="name" placeholder="Staff Name">
            <button type="submit">Add Staff</button>
        </form>
    '''


# ---------- RUN ----------
if __name__ == '__main__':
    app.run(debug=True)
