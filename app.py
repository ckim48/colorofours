from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory, jsonify
import sqlite3
import os
from werkzeug.utils import secure_filename
from changeImg import changeImage
from datetime import datetime


app = Flask(__name__)
app.secret_key = 'supersecretkey'
UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'processed'

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
if not os.path.exists(PROCESSED_FOLDER):
    os.makedirs(PROCESSED_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PROCESSED_FOLDER'] = PROCESSED_FOLDER

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload')
def upload():
    return render_template('upload.html')

@app.route('/donate')
def donate():
    return render_template('Donate.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/preview', methods=['POST'])
def preview():
    title = request.form['title']
    description = request.form['description']
    image = request.files['image']

    if image and title and description:
        filename = secure_filename(image.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        image.save(filepath)

        changeImage(filepath)

        original_image = url_for('orimg', filename=filename)
        prot_image = url_for('processed_file', filename='about_whatp.jpg')
        deut_image = url_for('processed_file', filename='about_whatd.jpg')
        trit_image = url_for('processed_file', filename='about_whatt.jpg')

        response = {
            'originalImage': original_image,
            'protImage': prot_image,
            'deutImage': deut_image,
            'tritImage': trit_image
        }

        return jsonify(response)
    else:
        return jsonify({'error': 'Please fill out all fields and upload an image.'}), 400

@app.route('/upload_image', methods=['POST'])
def upload_image():
    title = request.form['title']
    description = request.form['description']
    image = request.files['image']
    username = 'test'  # Replace this with session or user management system
    upload_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    if image and title and description:
        filename = secure_filename(image.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        image.save(filepath)

        changeImage(filepath)

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO images (title, description, filepath, username, upload_date, status)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (title, description, filepath, username, upload_date, 'pending'))
        conn.commit()
        conn.close()

        response = {
            'protImage': url_for('processed_file', filename='about_whatp.jpg'),
            'deutImage': url_for('processed_file', filename='about_whatd.jpg'),
            'tritImage': url_for('processed_file', filename='about_whatt.jpg')
        }

        return jsonify(response)
    else:
        return jsonify({'error': 'Please fill out all fields and upload an image.'}), 400


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/processed/<filename>')
def processed_file(filename):
    return send_from_directory(app.config['PROCESSED_FOLDER'], filename)

@app.route('/orimg/<filename>')
def orimg(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/admin')
def admin():
    conn = get_db_connection()
    images = conn.execute('SELECT * FROM images WHERE status = "pending"').fetchall()
    conn.close()
    return render_template('admin.html', images=images)

@app.route('/accept/<int:image_id>')
def accept(image_id):
    conn = get_db_connection()
    conn.execute('UPDATE images SET status = ? WHERE id = ?', ('accepted', image_id))
    conn.commit()
    conn.close()
    flash('Image accepted successfully!', 'success')
    return redirect(url_for('admin'))

@app.route('/reject/<int:image_id>')
def reject(image_id):
    conn = get_db_connection()
    conn.execute('UPDATE images SET status = ? WHERE id = ?', ('rejected', image_id))
    conn.commit()
    conn.close()
    flash('Image rejected successfully!', 'danger')
    return redirect(url_for('admin'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)
