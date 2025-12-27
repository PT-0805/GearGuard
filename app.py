from flask import Flask
from routes.auth import auth_bp
from routes.dashboard import dashboard_bp

app = Flask(__name__)
app.secret_key = "super_secret_key_for_session" # Needed for login sessions

# Register the blueprints (the split files)
app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)

if __name__ == '__main__':
    app.run(debug=True, port=5000)