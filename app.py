from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from datetime import datetime
import json
from admin_panel import *

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Измените на безопасный ключ

# Настройка Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id, username, password_hash):
        self.id = id
        self.username = username
        self.password_hash = password_hash

@login_manager.user_loader
def load_user(user_id):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    if user:
        return User(user['id'], user['username'], user['password_hash'])
    return None

@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()
        
        if user and check_password_hash(user['password_hash'], password):
            user_obj = User(user['id'], user['username'], user['password_hash'])
            login_user(user_obj)
            return redirect(url_for('index'))
        
        flash('Неверное имя пользователя или пароль')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/components')
@login_required
def components():
    components = get_all_components()
    categories = get_component_categories()
    return render_template('components.html', components=components, categories=categories)

@app.route('/builds')
@login_required
def builds():
    builds = get_all_builds()
    device_types = get_device_types()
    return render_template('builds.html', builds=builds, device_types=device_types)

@app.route('/add_component', methods=['POST'])
@login_required
def add_component_route():
    try:
        component_id = add_component(
            name=request.form['name'],
            category_id=request.form['category_id'],
            price=request.form['price'],
            price_category_id=request.form['price_category_id'],
            description=request.form['description'],
            specs=json.loads(request.form['specs']) if request.form['specs'] else None,
            image_url=request.form['image_url']
        )
        return jsonify({'success': True, 'id': component_id})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/add_build', methods=['POST'])
@login_required
def add_build_route():
    try:
        build_id = add_build(
            name=request.form['name'],
            device_type_id=request.form['device_type_id'],
            price_category_id=request.form['price_category_id'],
            description=request.form['description'],
            component_ids=json.loads(request.form['component_ids']),
            image_url=request.form['image_url']
        )
        return jsonify({'success': True, 'id': build_id})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True) 