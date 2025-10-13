import os
import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, send_file, jsonify
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import secrets

app = Flask(__name__)
app.secret_key = os.environ.get('SESSION_SECRET', secrets.token_hex(16))
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


def get_db():
    db = sqlite3.connect('dms.db')
    db.row_factory = sqlite3.Row
    return db


def init_db():
    db = get_db()
    db.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        department TEXT,
        name TEXT
    )''')

    db.execute('''CREATE TABLE IF NOT EXISTS documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        quantity TEXT,
        material_number TEXT,
        material_name TEXT,
        vendor TEXT,
        document_number TEXT,
        revision_number TEXT,
        price TEXT,
        date TEXT,
        status TEXT
    )''')

    db.execute('''CREATE TABLE IF NOT EXISTS uploads (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        document_number TEXT,
        revision_number TEXT,
        date TEXT,
        filename TEXT,
        filepath TEXT,
        uploaded_by TEXT
    )''')

    db.execute('''CREATE TABLE IF NOT EXISTS downloads (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        upload_id INTEGER,
        document_number TEXT,
        downloaded_by TEXT,
        download_date TEXT,
        FOREIGN KEY (upload_id) REFERENCES uploads(id)
    )''')

    admin_exists = db.execute('SELECT * FROM users WHERE username = ?', ('admin',)).fetchone()
    if not admin_exists:
        hashed_password = generate_password_hash('admin123')
        db.execute('INSERT INTO users (username, password, department, name) VALUES (?, ?, ?, ?)',
                   ('admin', hashed_password, 'Administration', 'Administrator'))

    db.commit()
    db.close()


@app.route('/')
def index():
    if 'user' in session:
        return redirect(url_for('menu'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        db = get_db()
        user = db.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        db.close()

        if user and check_password_hash(user['password'], password):
            session['user'] = username
            return redirect(url_for('menu'))
        else:
            return render_template('login.html', error='Invalid credentials')

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))


@app.route('/menu')
def menu():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('menu.html')


@app.route('/master/documents', methods=['GET', 'POST'])
def master_documents():
    if 'user' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        # Top-level fields (shared across all line items)
        document_number = request.form.get('document_number', '')
        revision_number = request.form.get('revision_number', '')
        status = request.form.get('status', 'ACTIVE')

        # Line item arrays
        quantities = request.form.getlist('quantity[]')
        material_numbers = request.form.getlist('material_number[]')
        material_names = request.form.getlist('material_name[]')
        vendors = request.form.getlist('vendor[]')
        prices = request.form.getlist('price[]')

        now = datetime.now().strftime('%Y-%m-%d')

        db = get_db()

        # Insert one row per line item (skip completely empty rows)
        for q, mn, mname, v, p in zip(quantities, material_numbers, material_names, vendors, prices):
            if any([q.strip(), mn.strip(), mname.strip(), v.strip(), p.strip()]):
                db.execute('''INSERT INTO documents 
                              (quantity, material_number, material_name, vendor, 
                               document_number, revision_number, price, date, status) 
                              VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                           (q.strip(), mn.strip(), mname.strip(), v.strip(),
                            document_number.strip(), revision_number.strip(), p.strip(), now, status))

        db.commit()
        db.close()

        return redirect(url_for('master_documents'))

    db = get_db()
    documents = db.execute('SELECT * FROM documents ORDER BY id DESC').fetchall()
    db.close()

    return render_template('master_documents.html', documents=documents)


@app.route('/master/documents/edit/<int:doc_id>', methods=['GET', 'POST'])
def edit_document(doc_id):
    if 'user' not in session:
        return redirect(url_for('login'))

    db = get_db()

    if request.method == 'POST':
        document_number = request.form.get('document_number', '')
        revision_number = request.form.get('revision_number', '')
        status = request.form.get('status', 'ACTIVE')

        quantities = request.form.getlist('quantity[]')
        material_numbers = request.form.getlist('material_number[]')
        material_names = request.form.getlist('material_name[]')
        vendors = request.form.getlist('vendor[]')
        prices = request.form.getlist('price[]')

        now = datetime.now().strftime('%Y-%m-%d')

        db.execute('DELETE FROM documents WHERE id = ?', (doc_id,))

        for q, mn, mname, v, p in zip(quantities, material_numbers, material_names, vendors, prices):
            if any([q.strip(), mn.strip(), mname.strip(), v.strip(), p.strip()]):
                db.execute('''INSERT INTO documents 
                              (quantity, material_number, material_name, vendor, 
                               document_number, revision_number, price, date, status) 
                              VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                           (q.strip(), mn.strip(), mname.strip(), v.strip(),
                            document_number.strip(), revision_number.strip(), p.strip(), now, status))

        db.commit()
        db.close()

        return redirect(url_for('master_documents'))

    document = db.execute('SELECT * FROM documents WHERE id = ?', (doc_id,)).fetchone()
    db.close()

    return render_template('edit_document.html', document=document)


@app.route('/master/documents/delete/<int:doc_id>')
def delete_document(doc_id):
    if 'user' not in session:
        return redirect(url_for('login'))

    db = get_db()
    db.execute('DELETE FROM documents WHERE id = ?', (doc_id,))
    db.commit()
    db.close()

    return redirect(url_for('master_documents'))


@app.route('/master/users', methods=['GET', 'POST'])
def master_users():
    if 'user' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        department = request.form['department']
        name = request.form['name']

        db = get_db()
        hashed_password = generate_password_hash(password)
        try:
            db.execute('INSERT INTO users (username, password, department, name) VALUES (?, ?, ?, ?)',
                       (username, hashed_password, department, name))
            db.commit()
        except sqlite3.IntegrityError:
            pass
        db.close()

        return redirect(url_for('master_users'))

    db = get_db()
    users = db.execute('SELECT * FROM users').fetchall()
    db.close()

    return render_template('master_users.html', users=users)


@app.route('/master/users/edit/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    if 'user' not in session:
        return redirect(url_for('login'))

    db = get_db()

    if request.method == 'POST':
        username = request.form['username']
        password = request.form.get('password', '')
        department = request.form['department']
        name = request.form['name']

        if password:
            hashed_password = generate_password_hash(password)
            db.execute('''UPDATE users SET username=?, password=?, department=?, name=? 
                          WHERE id=?''',
                       (username, hashed_password, department, name, user_id))
        else:
            db.execute('''UPDATE users SET username=?, department=?, name=? 
                          WHERE id=?''',
                       (username, department, name, user_id))

        db.commit()
        db.close()

        return redirect(url_for('master_users'))

    user_data = db.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    db.close()

    return render_template('edit_user.html', user=user_data)


@app.route('/master/users/delete/<int:user_id>')
def delete_user(user_id):
    if 'user' not in session:
        return redirect(url_for('login'))

    db = get_db()
    db.execute('DELETE FROM users WHERE id = ?', (user_id,))
    db.commit()
    db.close()

    return redirect(url_for('master_users'))


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'user' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        document_number = request.form['document_number']
        revision_number = request.form['revision_number']
        file = request.files.get('file')

        if file and file.filename:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            db = get_db()
            db.execute('''INSERT INTO uploads (document_number, revision_number, 
                          date, filename, filepath, uploaded_by) 
                          VALUES (?, ?, ?, ?, ?, ?)''',
                       (document_number, revision_number,
                        datetime.now().strftime('%Y-%m-%d'),
                        filename, filepath, session['user']))
            db.commit()
            db.close()

        return redirect(url_for('upload'))

    return render_template('upload.html')


@app.route('/download', methods=['GET', 'POST'])
def download():
    if 'user' not in session:
        return redirect(url_for('login'))

    results = []
    if request.method == 'POST':
        document_number = request.form.get('document_number', '')
        revision_number = request.form.get('revision_number', '')

        db = get_db()
        query = 'SELECT * FROM uploads WHERE 1=1'
        params = []

        if document_number:
            query += ' AND document_number LIKE ?'
            params.append(f'%{document_number}%')
        if revision_number:
            query += ' AND revision_number LIKE ?'
            params.append(f'%{revision_number}%')

        results = db.execute(query, params).fetchall()
        db.close()

    return render_template('download.html', results=results)


@app.route('/download_file/<int:upload_id>')
def download_file(upload_id):
    if 'user' not in session:
        return redirect(url_for('login'))

    db = get_db()
    upload = db.execute('SELECT * FROM uploads WHERE id = ?', (upload_id,)).fetchone()

    if upload:
        db.execute('''INSERT INTO downloads (upload_id, document_number, downloaded_by, download_date) 
                      VALUES (?, ?, ?, ?)''',
                   (upload_id, upload['document_number'], session['user'],
                    datetime.now().strftime('%Y-%m-%d')))
        db.commit()
        db.close()

        return send_file(upload['filepath'], as_attachment=True, download_name=upload['filename'])

    db.close()
    return redirect(url_for('download'))


@app.route('/view_report')
def view_report():
    if 'user' not in session:
        return redirect(url_for('login'))

    document_number = request.args.get('document_number', '')
    revision_number = request.args.get('revision_number', '')
    date = request.args.get('date', '')
    material_name = request.args.get('material_name', '')

    db = get_db()

    query = 'SELECT * FROM documents WHERE 1=1'
    params = []

    if document_number:
        query += ' AND document_number LIKE ?'
        params.append(f'%{document_number}%')
    if revision_number:
        query += ' AND revision_number LIKE ?'
        params.append(f'%{revision_number}%')
    if date:
        query += ' AND date LIKE ?'
        params.append(f'%{date}%')
    if material_name:
        query += ' AND material_name LIKE ?'
        params.append(f'%{material_name}%')

    documents = db.execute(query, params).fetchall()

    uploads = db.execute('SELECT * FROM uploads').fetchall()

    downloads = db.execute('''SELECT d.*, u.filename, u.document_number 
                              FROM downloads d 
                              JOIN uploads u ON d.upload_id = u.id''').fetchall()

    db.close()

    return render_template('view_report.html', documents=documents, uploads=uploads, downloads=downloads)


@app.route('/api/search_documents')
def search_documents():
    term = request.args.get('term', '')
    db = get_db()

    results = db.execute('''SELECT DISTINCT document_number, revision_number 
                            FROM documents 
                            WHERE document_number LIKE ? OR revision_number LIKE ?
                            LIMIT 10''', (f'%{term}%', f'%{term}%')).fetchall()

    db.close()

    suggestions = []
    for row in results:
        suggestions.append({
            'document_number': row['document_number'],
            'revision_number': row['revision_number']
        })

    return jsonify(suggestions)


if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)