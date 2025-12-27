from flask import Flask, render_template, request
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# --- DATABASE SETUP ---
# YOUR PROVIDED URI
MONGO_URI = "mongodb+srv://dbUserrr:MyPassisSafe@cluster0.ldlhqan.mongodb.net/?appName=Cluster0"

try:
    client = MongoClient(MONGO_URI)
    # Using a database named 'user_system_db' (it will auto-create if not exists)
    db = client.user_system_db
    users_collection = db.users
    print("Connected to MongoDB successfully!")
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")

# --- ROUTES ---

@app.route('/')
def home():
    # Renders the html file from the templates folder
    return render_template('index.html')

@app.route('/signup', methods=['POST'])
def signup():
    # 1. Get data from HTML form
    name = request.form.get('name')
    email = request.form.get('email')
    password = request.form.get('password')
    retype_password = request.form.get('retype_password')

    # 2. Basic Validation
    if password != retype_password:
        return "Error: Passwords do not match! <a href='/'>Go back</a>"
    
    # 3. Check if user already exists
    if users_collection.find_one({"email": email}):
        return "Error: Email already exists! <a href='/'>Go back</a>"

    # 4. Hash password (Security best practice) and Save
    hashed_password = generate_password_hash(password)
    
    users_collection.insert_one({
        "name": name,
        "email": email,
        "password": hashed_password
    })

    return "Signup Successful! Please log in below. <a href='/'>Go back</a>"

@app.route('/login', methods=['POST'])
def login():
    # 1. Get data
    email = request.form.get('email')
    password = request.form.get('password')

    # 2. Find user in MongoDB
    user = users_collection.find_one({"email": email})

    # 3. Check password
    if user and check_password_hash(user['password'], password):
        return f"<h1>Welcome, {user['name']}!</h1> <p>Login Successful.</p>"
    else:
        return "Invalid email or password. <a href='/'>Try again</a>"

if __name__ == '__main__':
    app.run(debug=True, port=5000)