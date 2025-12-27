from flask import Blueprint, request, render_template, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_db

# Create a Blueprint (a group of routes)
auth_bp = Blueprint('auth', __name__)
db = get_db()

@auth_bp.route('/')
def home():
    if 'user' in session:
        return redirect(url_for('dashboard.view_dashboard'))
    return render_template('index.html')

@auth_bp.route('/signup', methods=['POST'])
def signup():
    name = request.form.get('name')
    email = request.form.get('email')
    password = request.form.get('password')
    retype_password = request.form.get('retype_password')

    if password != retype_password:
        return "Error: Passwords do not match!"
    
    if db.users.find_one({"email": email}):
        return "Error: Email already exists!"

    hashed_password = generate_password_hash(password)
    db.users.insert_one({
        "name": name, 
        "email": email, 
        "password": hashed_password
    })
    return "Signup Successful! <a href='/'>Log in</a>"

@auth_bp.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')

    user = db.users.find_one({"email": email})

    if user and check_password_hash(user['password'], password):
        # Save user in session so they stay logged in
        session['user'] = user['name']
        return redirect(url_for('dashboard.view_dashboard'))
    else:
        return "Invalid credentials"

@auth_bp.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('auth.home'))