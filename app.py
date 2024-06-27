from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
from changeImg import changeImage
app = Flask(__name__)
app.secret_key = 'supersecretkey'

def get_user(username, password):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM users WHERE username = ? AND password = ?
    ''', (username, password))
    user = cursor.fetchone()
    conn.close()
    return user

@app.route('/donate')
def donate():
    return render_template('Donate.html')

@app.route('/upload')
def upload():
    return render_template('upload.html')

def user_exists(username):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM users WHERE username = ?
    ''', (username,))
    user = cursor.fetchone()
    conn.close()
    return user

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/overview')
def overview():
    if 'user' in session:
        return render_template('overview.html')
    else:
        flash('You need to log in first.', 'danger')
        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = get_user(username, password)

        if user:
            session['user'] = username
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        repassword = request.form['repassword']
        fullname = request.form['fullname']
        email = request.form['email']
        phone = request.form['phone']

        if user_exists(username):
            flash('Username already exists.', 'danger')
            return redirect(url_for('register'))

        if password != repassword:
            flash('Passwords do not match. Please try again.', 'danger')
            return redirect(url_for('register'))

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO users (username, password, name, email, phone)
            VALUES (?, ?, ?, ?, ?)
        ''', (username, password, fullname, email, phone))
        conn.commit()
        conn.close()

        flash('Registration successful!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

if __name__ == '__main__':
    app.run(debug=True, port=8080)
