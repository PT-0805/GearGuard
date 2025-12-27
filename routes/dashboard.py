from flask import Blueprint, render_template, session, redirect, url_for
from database import get_db

dashboard_bp = Blueprint('dashboard', __name__)
db = get_db()

@dashboard_bp.route('/dashboard')
def view_dashboard():
    # 1. Security Check
    if 'user' not in session:
        return redirect(url_for('auth.home'))
    
    # --- FETCH & CALCULATE KPI DATA ---
    
    # Red Card: Count equipment with health < 30
    critical_count = db.equipment.count_documents({"health": {"$lt": 30}})
    
    # Blue Card: Calculate average technician load
    techs = list(db.technicians.find())
    if len(techs) > 0:
        total_load = sum(t.get('current_load', 0) for t in techs)
        avg_load = int(total_load / len(techs))
    else:
        avg_load = 0

    # Green Card: Count open and overdue requests
    # "ne" means "not equal" to Closed
    open_requests_count = db.requests.count_documents({"stage": {"$ne": "Closed"}})
    overdue_count = db.requests.count_documents({"is_overdue": True})

    # Pack data for the HTML
    kpi_data = {
        "critical_count": critical_count,
        "critical_health": "< 30%",
        "tech_load": f"{avg_load}%",
        "open_requests": open_requests_count,
        "overdue": overdue_count
    }

    # --- FETCH TABLE DATA ---
    requests_list = list(db.requests.find())

    return render_template('dashboard.html', 
                           user=session['user'], 
                           kpi=kpi_data, 
                           requests=requests_list)