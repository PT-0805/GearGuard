from flask import Blueprint, render_template, session, redirect, url_for
from database import get_db

dashboard_bp = Blueprint('dashboard', __name__)
db = get_db()

# NEW API ROUTE TO FETCH SINGLE REQUEST DETAILS
@dashboard_bp.route('/api/request/<request_id>')
def get_request_details(request_id):
    if 'user' not in session: return jsonify({"error": "Unauthorized"}), 401
    
    req = db.requests.find_one({"_id": ObjectId(request_id)})
    if req:
        req['_id'] = str(req['_id'])
        req['equipment_id'] = str(req.get('equipment_id', ''))
        # Return the specific new fields
        req['notes'] = req.get('notes', '') 
        req['status_state'] = req.get('status_state', 'in_progress')
        
        if 'scheduled_date' in req and req['scheduled_date']:
            req['scheduled_date'] = req['scheduled_date'].strftime("%Y-%m-%d %H:%M")
        return jsonify(req)
    else:
        return jsonify({"error": "Not found"}), 404

# NEW: Generic Update Route (Auto-save)
@dashboard_bp.route('/api/request/update', methods=['POST'])
def update_request():
    if 'user' not in session: return jsonify({"error": "Unauthorized"}), 401
    
    data = request.json
    req_id = data.get('id')
    field = data.get('field')  # e.g., 'notes' or 'status_state'
    value = data.get('value')

    if not req_id or not field:
        return jsonify({"error": "Missing data"}), 400

    # Update the database immediately
    db.requests.update_one(
        {"_id": ObjectId(req_id)},
        {"$set": {field: value}}
    )
    
    return jsonify({"success": True})

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
    requests_list = list(db.requests.find())
    
    # Dummy KPI data to prevent errors if you copy-paste this block alone
    kpi_data = {"critical_count": 5, "tech_load": 85, "open_requests": 12, "overdue": 3} 

    # --- FETCH TABLE DATA ---
    requests_list = list(db.requests.find())

    return render_template('dashboard.html', 
                           user=session['user'], 
                           kpi=kpi_data, 
                           requests=requests_list)