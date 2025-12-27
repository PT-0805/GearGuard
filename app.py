from flask import Flask
from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.pages import pages_bp   # <--- 1. IMPORT THE NEW FILE

app = Flask(__name__)
app.secret_key = "super_secret_key_for_session"

# Register Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(pages_bp)    # <--- 2. REGISTER THE BLUEPRINT

if __name__ == '__main__':
    app.run(debug=True, port=5000)