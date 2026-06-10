from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import sqlite3
import os
import uuid

app = Flask(__name__)
CORS(app)
app.config['JSON_AS_ASCII'] = False

DB_PATH = 'miuki.db'
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ───── ТОВАРЫ ─────

@app.route('/api/products', methods=['GET'])
def get_products():
    category = request.args.get('category')
    search   = request.args.get('search')
    conn = get_db()
    query  = 'SELECT * FROM products WHERE 1=1'
    params = []
    if category:
        query += ' AND category = ?'
        params.append(category)
    if search:
        query += ' AND (name LIKE ? OR description LIKE ?)'
        params += [f'%{search}%', f'%{search}%']
    query += ' ORDER BY id DESC'
    products = conn.execute(query, params).fetchall()
    conn.close()
    return jsonify([dict(p) for p in products])


@app.route('/api/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    conn = get_db()
    product = conn.execute('SELECT * FROM products WHERE id = ?', (product_id,)).fetchone()
    conn.close()
    if not product:
        return jsonify({'error': 'Товар не найден'}), 404
    return jsonify(dict(product))


@app.route('/api/products', methods=['POST'])
def add_product():
    data = request.form
    image_url = ''

    if 'image' in request.files:
        file = request.files['image']
        if file.filename:
            ext      = os.path.splitext(file.filename)[1]
            filename = f'{uuid.uuid4()}{ext}'
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            image_url = f'/uploads/{filename}'

    conn = get_db()
    conn.execute(
        '''INSERT INTO products (name, category, price, description, image_url, in_stock)
           VALUES (?, ?, ?, ?, ?, ?)''',
        (
            data.get('name'),
            data.get('category'),
            float(data.get('price', 0)),
            data.get('description', ''),
            image_url,
            1 if data.get('in_stock', 'true') == 'true' else 0,
        )
    )
    conn.commit()
    conn.close()
    return jsonify({'success': True}), 201


@app.route('/api/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    data = request.form
    conn = get_db()
    product   = conn.execute('SELECT * FROM products WHERE id = ?', (product_id,)).fetchone()
    image_url = dict(product)['image_url']

    if 'image' in request.files:
        file = request.files['image']
        if file.filename:
            ext      = os.path.splitext(file.filename)[1]
            filename = f'{uuid.uuid4()}{ext}'
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            image_url = f'/uploads/{filename}'

    conn.execute(
        '''UPDATE products SET name=?, category=?, price=?, description=?, image_url=?, in_stock=?
           WHERE id=?''',
        (
            data.get('name'),
            data.get('category'),
            float(data.get('price', 0)),
            data.get('description', ''),
            image_url,
            1 if data.get('in_stock', 'true') == 'true' else 0,
            product_id,
        )
    )
    conn.commit()
    conn.close()
    return jsonify({'success': True})


@app.route('/api/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    conn = get_db()
    conn.execute('DELETE FROM products WHERE id = ?', (product_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})


# ───── КАТЕГОРИИ ─────

@app.route('/api/categories', methods=['GET'])
def get_categories():
    conn       = get_db()
    categories = conn.execute('SELECT DISTINCT category FROM products').fetchall()
    conn.close()
    return jsonify([c['category'] for c in categories])


# ───── ЗАГРУЗКА ФОТО ─────

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


from functools import wraps
from flask import request, Response

def check_auth(username, password):
    return username == 'miuki_adm_20' and password == 'FJGNIMIUKI'

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return Response(
                'Доступ запрещён',
                401,
                {'WWW-Authenticate': 'Basic realm="Miuki Admin"'}
            )
        return f(*args, **kwargs)
    return decorated

@app.route('/admin')
@requires_auth
def admin():
    return send_from_directory('.', 'admin.html')

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
