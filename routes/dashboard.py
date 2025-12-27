from flask import Blueprint, render_template, session, redirect, url_for
from database import get_db

dashboard_bp = Blueprint('dashboard', __name__)
db = get_db()

@dashboard_bp.route('/dashboard')
def view_dashboard():
    if 'user' not in session:
        return redirect(url_for('auth.home'))
    
    # --- FETCH DATA FOR CARDS ---
    # In a real app, you would count these from the DB. 
    # For now, we hardcode the counts to match your wireframe image.
    kpi_data = {
        "critical_count": 5,
        "critical_health": "< 30%",
        "tech_load": "85%",
        "open_requests": 12,
        "overdue": 3
    }

    # --- FETCH DATA FOR TABLE ---
    # Let's get actual data from MongoDB "requests" collection
    # If empty, we insert dummy data for testing
    if db.requests.count_documents({}) == 0:
        db.requests.insert_many([
            {"subject": "Test activity", "employee": "Mitchell Admin", "technician": "Aka Foster", "category": "computer", "stage": "New Request", "company": "My company"},
            {"subject": "Fix Printer", "employee": "Sarah Jones", "technician": "Bob Smith", "category": "hardware", "stage": "In Progress", "company": "TechCorp"},
        ])
    
    requests_list = list(db.requests.find())

    return render_template('dashboard.html', 
                           user=session['user'], 
                           kpi=kpi_data, 
                           requests=requests_list)