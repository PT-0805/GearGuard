from flask import Blueprint, render_template, session, redirect, url_for, jsonify, request
from bson.objectid import ObjectId
from datetime import datetime
from database import get_db

dashboard_bp = Blueprint('dashboard', __name__)
db = get_db()

@dashboard_bp.route('/dashboard')
def view_dashboard():
    if 'user' not in session: return redirect(url_for('auth.home'))
    
    # --- KPI Calculations ---
    critical_count = db.equipment.count_documents({"health": {"$lt": 30}})
    open_requests_count = db.requests.count_documents({"stage": {"$nin": ["Repaired", "Scrap"]}})
    
    # Technician load calculation
    techs = list(db.technicians.find())
    avg_load = int(sum(t.get('current_load', 0) for t in techs) / len(techs)) if techs else 85
    overdue_count = db.requests.count_documents({"is_overdue": True})

    kpi_summary = {
        "critical_count": critical_count, 
        "tech_load": avg_load, 
        "open_requests": open_requests_count, 
        "overdue": overdue_count
    }

    # --- Dropdown Data ---
    # We fetch 'category' for Equipment so the JS can auto-fill it in the modal
    equipment_options = list(db.equipment.find({}, {"name": 1, "category": 1}))
    work_center_options = list(db.work_centers.find({}, {"name": 1}))
    technician_options = list(db.users.find({}, {"name": 1}))
    team_options = list(db.teams.find({}, {"name": 1}))
    company_options = ["My Company (San Francisco)", "My Company (New York)"]

    # --- Table Data ---
    requests_list = list(db.requests.find().sort("_id", -1))

    return render_template('dashboard.html', 
                           user=session['user'], 
                           kpi=kpi_summary, 
                           requests=requests_list,
                           equipment_options=equipment_options,
                           work_center_options=work_center_options,
                           technician_options=technician_options,
                           team_options=team_options,
                           company_options=company_options,
                           active_page='dashboard')

# --- API ROUTES ---

@dashboard_bp.route('/api/request/<request_id>')
def get_request_details(request_id):
    """Fetches details for 'View' mode, including Target Type logic."""
    if 'user' not in session: return jsonify({"error": "Unauthorized"}), 401
    try:
        req = db.requests.find_one({"_id": ObjectId(request_id)})
        if req:
            req['_id'] = str(req['_id'])
            # Convert ObjectIds to strings for JSON
            if 'equipment_id' in req and req['equipment_id']: 
                req['equipment_id'] = str(req['equipment_id'])
            if 'work_center_id' in req and req['work_center_id']: 
                req['work_center_id'] = str(req['work_center_id'])
            
            # Ensure defaults for empty fields
            req['priority'] = req.get('priority', 'low')
            req['instructions'] = req.get('instructions', '')
            req['notes'] = req.get('notes', '')
            
            if 'scheduled_date' in req and req['scheduled_date']:
                req['scheduled_date'] = req['scheduled_date'].strftime("%Y-%m-%dT%H:%M")
            
            return jsonify(req)
        return jsonify({"error": "Not found"}), 404
    except Exception as e: 
        return jsonify({"error": str(e)}), 400

@dashboard_bp.route('/api/request/save', methods=['POST'])
def save_request():
    """Unified route to handle target switching and saving."""
    if 'user' not in session: return redirect(url_for('auth.home'))
    
    req_id = request.form.get('request_id')
    target_type = request.form.get('target_type') # 'equipment' or 'work_center'
    
    # Parse Scheduled Date
    sched_date_str = request.form.get('scheduled_date')
    sched_date = datetime.strptime(sched_date_str, "%Y-%m-%dT%H:%M") if sched_date_str else None

    # Base data structure
    data = {
        "subject": request.form.get('subject'),
        "target_type": target_type,
        "technician": request.form.get('technician'),
        "team": request.form.get('team'),
        "category": request.form.get('category'),
        "type": request.form.get('m_type'),
        "priority": request.form.get('priority'),
        "scheduled_date": sched_date,
        "duration": request.form.get('duration'),
        "company": request.form.get('company'),
        "notes": request.form.get('notes'),
        "instructions": request.form.get('instructions')
    }

    # Handle Target Logic
    if target_type == 'equipment':
        eq_id = request.form.get('equipment')
        eq_obj = db.equipment.find_one({"_id": ObjectId(eq_id)}) if eq_id else None
        data["equipment_id"] = ObjectId(eq_id) if eq_id else None
        data["equipment_name"] = eq_obj['name'] if eq_obj else "Unknown"
        data["work_center_id"] = None # Clear WC if it's equipment
    else:
        wc_id = request.form.get('work_center')
        wc_obj = db.work_centers.find_one({"_id": ObjectId(wc_id)}) if wc_id else None
        data["work_center_id"] = ObjectId(wc_id) if wc_id else None
        data["work_center_name"] = wc_obj['name'] if wc_obj else "Unknown Area"
        data["equipment_id"] = None # Clear Eq if it's a Work Center

    if req_id:
        db.requests.update_one({"_id": ObjectId(req_id)}, {"$set": data})
    else:
        data["employee"] = session['user']
        data["stage"] = "New Request"
        data["status_color"] = "grey"
        data["is_overdue"] = False
        db.requests.insert_one(data)
    
    return redirect(url_for('dashboard.view_dashboard'))

@dashboard_bp.route('/api/request/update', methods=['POST'])
def update_request():
    """Real-time auto-save for priority, notes, and status."""
    data = request.json
    db.requests.update_one({"_id": ObjectId(data['id'])}, {"$set": {data['field']: data['value']}})
    return jsonify({"success": True})

@dashboard_bp.route('/api/request/delete/<request_id>', methods=['POST'])
def delete_request(request_id):
    if 'user' not in session: return jsonify({"error": "Unauthorized"}), 401
    db.requests.delete_one({"_id": ObjectId(request_id)})
    return redirect(url_for('dashboard.view_dashboard'))

# Add this specific route for Kanban/Stage transitions
@dashboard_bp.route('/api/request/update-stage', methods=['POST'])
def update_request_stage():
    if 'user' not in session: return jsonify({"error": "Unauthorized"}), 401
    data = request.json
    # Stages: "New Request", "In Progress", "Done", "Scrapped"
    db.requests.update_one(
        {"_id": ObjectId(data['id'])}, 
        {"$set": {"stage": data['stage']}}
    )
    return jsonify({"success": True})