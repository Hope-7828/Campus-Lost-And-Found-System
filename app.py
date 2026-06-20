from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename
import os
import sqlite3
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# ---------------- DATABASE ---------------- #
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    # Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        is_admin INTEGER DEFAULT 0
    )''')

    # Lost items table
    c.execute('''CREATE TABLE IF NOT EXISTS lost_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        item_name TEXT,
        description TEXT,
        image TEXT
    )''')

    # Payments table
    c.execute('''CREATE TABLE IF NOT EXISTS payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        amount REAL,
        phone TEXT,
        mpesa_receipt TEXT,
        status TEXT DEFAULT 'Pending',
        used INTEGER DEFAULT 0,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')

    conn.commit()
    conn.close()


def create_default_admin():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    # Default admin credentials
    admin_username = "admin"
    admin_email = "hope123@gmail.com"
    admin_password = "mwaura123"  # <-- admin password

    # Check if admin already exists
    c.execute("SELECT * FROM users WHERE email=?", (admin_email,))
    if not c.fetchone():
        c.execute(
            "INSERT INTO users (username, email, password, is_admin) VALUES (?, ?, ?, ?)",
            (admin_username, admin_email, admin_password, 1)
        )
        print(f"Default admin created: {admin_email} / {admin_password}")

    conn.commit()
    conn.close()


# Initialize database and default admin
init_db()
create_default_admin()

# ---------------- HOME ---------------- #
@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return redirect(url_for('home'))


@app.route('/home')
def home():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    c.execute("""
        SELECT lost_items.id, users.username, users.email, lost_items.item_name, lost_items.description, lost_items.image
        FROM lost_items
        JOIN users ON lost_items.user_id = users.id
    """)
    items = c.fetchall()
    conn.close()

    return render_template('home.html', items=items)


# ---------------- AUTH ---------------- #
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        conn = sqlite3.connect('database.db')
        c = conn.cursor()

        c.execute("SELECT * FROM users WHERE email=?", (email,))
        existing_user = c.fetchone()

        if existing_user:
            flash("Email already registered. Please login or use another email.")
            conn.close()
            return redirect(url_for('register'))

        c.execute(
            "INSERT INTO users (username,email,password,is_admin) VALUES (?,?,?,?)",
            (username, email, password, 0)
        )
        conn.commit()
        conn.close()

        flash("Registered successfully!")
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        conn = sqlite3.connect('database.db')
        c = conn.cursor()

        c.execute(
            "SELECT * FROM users WHERE email=? AND password=?",
            (request.form['email'], request.form['password'])
        )

        user = c.fetchone()
        conn.close()

        if user:
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['is_admin'] = user[4]

            # Redirect admin to dashboard
            if user[4] == 1:
                return redirect(url_for('admin_dashboard'))

            # Redirect normal users
            return redirect(url_for('home'))

        flash("Invalid credentials")

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


# ---------------- FAKE PAYMENT ---------------- #
@app.route('/pay')
def pay():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    c.execute("SELECT * FROM payments WHERE user_id=? AND status='Completed' AND used=0",
              (session['user_id'],))
    existing = c.fetchone()

    if existing:
        flash("You already have an unused payment.")
        conn.close()
        return redirect(url_for('report'))

    c.execute("INSERT INTO payments (user_id, amount, status, used) VALUES (?, ?, ?, ?)",
              (session['user_id'], 150, "Completed", 0))

    conn.commit()
    conn.close()

    flash("Payment of 150 KES successful (Demo).")
    return redirect(url_for('report'))


# ---------------- REPORT ---------------- #
@app.route('/report', methods=['GET', 'POST'])
def report():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    c.execute("SELECT * FROM payments WHERE user_id=? AND status='Completed' AND used=0",
              (session['user_id'],))
    payment = c.fetchone()

    if request.method == 'POST':
        if not payment:
            flash("Please pay first.")
            return redirect(url_for('report'))

        name = request.form['name']
        description = request.form['description']
        image = request.files['image']

        filename = None
        if image and image.filename != '':
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        c.execute("INSERT INTO lost_items (user_id, item_name, description, image) VALUES (?, ?, ?, ?)",
                  (session['user_id'], name, description, filename))

        c.execute("UPDATE payments SET used=1 WHERE id=?", (payment[0],))
        conn.commit()
        conn.close()

        flash("Item reported successfully!")
        return redirect(url_for('home'))

    conn.close()
    return render_template('report.html', payment=payment)


# ---------------- PROFILE ---------------- #
@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    c.execute("SELECT * FROM lost_items WHERE user_id=?", (session['user_id'],))
    items = c.fetchall()

    c.execute("SELECT * FROM payments WHERE user_id=?", (session['user_id'],))
    payments = c.fetchall()
    conn.close()

    return render_template('profile.html',
                           username=session['username'],
                           items=items,
                           payments=payments)


@app.route('/profile/delete_item/<int:item_id>', methods=['POST'])
def delete_profile_item(item_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("DELETE FROM lost_items WHERE id=? AND user_id=?",
              (item_id, session['user_id']))
    conn.commit()
    conn.close()

    flash("Item deleted!")
    return redirect(url_for('profile'))


# ---------------- ADMIN DASHBOARD ---------------- #
@app.route('/admin')
def admin_dashboard():
    if 'user_id' not in session or session.get('is_admin') != 1:
        flash("Access denied.")
        return redirect(url_for('home'))

    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    try:
        c.execute("SELECT id, username, email, created_at FROM users ORDER BY created_at DESC")
        users = c.fetchall()
    except sqlite3.OperationalError:
        c.execute("SELECT id, username, email FROM users")
        users = c.fetchall()

    c.execute("""
        SELECT lost_items.id, users.username, users.email, lost_items.item_name, lost_items.description
        FROM lost_items
        JOIN users ON lost_items.user_id = users.id
    """)
    items = c.fetchall()

    c.execute("""
        SELECT payments.id, users.username, payments.amount, payments.status, payments.used
        FROM payments
        JOIN users ON payments.user_id = users.id
        ORDER BY payments.id DESC
    """)
    payments = c.fetchall()

    conn.close()

    return render_template('admin_dashboard.html',
                           users=users,
                           items=items,
                           payments=payments)


@app.route('/admin/payment_report')
def admin_payment_report():
    if 'user_id' not in session or session.get('is_admin') != 1:
        flash("Access denied.")
        return redirect(url_for('home'))

    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    c.execute("SELECT COUNT(*), SUM(amount) FROM payments WHERE status='Completed'")
    total_count, total_amount = c.fetchone()

    c.execute("SELECT COUNT(*), SUM(amount) FROM payments WHERE status='Pending'")
    pending_count, pending_amount = c.fetchone()

    conn.close()
    return render_template('admin_payment_report.html',
                           total_count=total_count,
                           total_amount=total_amount,
                           pending_count=pending_count,
                           pending_amount=pending_amount)


@app.route('/admin/delete_user/<int:user_id>', methods=['POST'])
def admin_delete_user(user_id):
    if 'user_id' not in session or session.get('is_admin') != 1:
        flash("Access denied.")
        return redirect(url_for('home'))

    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("DELETE FROM lost_items WHERE user_id=?", (user_id,))
    c.execute("DELETE FROM payments WHERE user_id=?", (user_id,))
    c.execute("DELETE FROM users WHERE id=?", (user_id,))
    conn.commit()
    conn.close()

    flash("User and all related data deleted successfully!")
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/delete_item/<int:item_id>', methods=['POST'])
def admin_delete_item(item_id):
    if 'user_id' not in session or session.get('is_admin') != 1:
        flash("Access denied.")
        return redirect(url_for('home'))

    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("DELETE FROM lost_items WHERE id=?", (item_id,))
    conn.commit()
    conn.close()

    flash("Lost item deleted successfully!")
    return redirect(url_for('admin_dashboard'))


# ---------------- ADMIN NEW ---------------- #
@app.route('/admin_new')
def admin_dashboard_new():
    if 'user_id' not in session or session.get('is_admin') != 1:
        flash("Access denied.")
        return redirect(url_for('home'))

    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT id, username, email FROM users")
    users = c.fetchall()

    c.execute("""
        SELECT lost_items.id, users.username, users.email, lost_items.item_name
        FROM lost_items
        JOIN users ON lost_items.user_id = users.id
    """)
    items = c.fetchall()
    conn.close()

    return render_template('admin_new.html', users=users, items=items)

# ---------------- CONTACT REPORTER ---------------- #
@app.route('/contact_reporter/<int:item_id>')
def contact_reporter(item_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    c.execute("""
        SELECT users.email, users.username, lost_items.item_name
        FROM lost_items
        JOIN users ON lost_items.user_id = users.id
        WHERE lost_items.id = ?
    """, (item_id,))

    reporter = c.fetchone()
    conn.close()

    if reporter:
        email = reporter[0]
        username = reporter[1]
        item_name = reporter[2]

        return render_template(
            'contact_reporter.html',
            email=email,
            username=username,
            item_name=item_name
        )

    flash("Reporter not found.")
    return redirect(url_for('home'))
# ---------------- MAIN ---------------- #
if __name__ == '__main__':
    app.run(debug=True)