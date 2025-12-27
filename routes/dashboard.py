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
    techs = list(db.technicians.find())
    avg_load = int(sum(t.get('current_load', 0) for t in techs) / len(techs)) if techs else 85
    overdue_count = db.requests.count_documents({"is_overdue": True})

    # --- Dropdown Data ---
    equipment_options = list(db.equipment.find({}, {"name": 1, "serial_number": 1}))
    technician_options = list(db.users.find({}, {"name": 1}))
    # Fetch teams for the new dropdown
    team_options = list(db.teams.find({}, {"name": 1}))
    # Hardcoded company options for now
    company_options = ["My Company (San Francisco)", "My Company (New York)", "Client Site A"]

    # --- Table Data ---
    requests_list = list(db.requests.find().sort("_id", -1))

    return render_template('dashboard.html', 
                           user=session['user'], 
                           kpi={"critical_count": critical_count, "tech_load": avg_load, "open_requests": open_requests_count, "overdue": overdue_count},
                           requests=requests_list,
                           equipment_options=equipment_options,
                           technician_options=technician_options,
                           team_options=team_options,
                           company_options=company_options,
                           active_page='dashboard')

# --- API ROUTES ---

@dashboard_bp.route('/api/request/<request_id>')
def get_request_details(request_id):
    """Fetches details for 'View' mode, including new fields."""
    if 'user' not in session: return jsonify({"error": "Unauthorized"}), 401
    try:
        req = db.requests.find_one({"_id": ObjectId(request_id)})
        if req:
            req['_id'] = str(req['_id'])
            if 'equipment_id' in req: req['equipment_id'] = str(req['equipment_id'])
            # Ensure new fields exist even if old records don't have them
            req['priority'] = req.get('priority', 'low')
            req['instructions'] = req.get('instructions', '')
            req['notes'] = req.get('notes', '')
            
            # Format date for the datetime-local input (YYYY-MM-DDTHH:MM)
            if 'scheduled_date' in req and req['scheduled_date']:
                req['scheduled_date'] = req['scheduled_date'].strftime("%Y-%m-%dT%H:%M")
            
            return jsonify(req)
        return jsonify({"error": "Not found"}), 404
    except Exception as e: print(e); return jsonify({"error": str(e)}), 400

@dashboard_bp.route('/api/request/add', methods=['POST'])
def add_request():
    """Saves a new request with all the new form fields."""
    if 'user' not in session: return redirect(url_for('auth.home'))
    
    eq_id = request.form.get('equipment')
    eq_obj = db.equipment.find_one({"_id": ObjectId(eq_id)}) if eq_id else None

    # Parse the date-time string from the form
    sched_date_str = request.form.get('scheduled_date')
    sched_date = datetime.strptime(sched_date_str, "%Y-%m-%dT%H:%M") if sched_date_str else None

    new_request = {
        "subject": request.form.get('subject'),
        "employee": session['user'],
        "equipment_id": ObjectId(eq_id) if eq_id else None,
        "equipment_name": eq_obj['name'] if eq_obj else "Unknown",
        "technician": request.form.get('technician'),
        "team": request.form.get('team'),           # NEW
        "category": request.form.get('category'),
        "type": request.form.get('m_type'),
        "priority": request.form.get('priority'),   # NEW
        "stage": "New Request",
        "status_color": "grey",
        "notes": request.form.get('notes'),
        "instructions": request.form.get('instructions'), # NEW
        "scheduled_date": sched_date, # NEW (parsed)
        "duration": request.form.get('duration'),   # NEW
        "company": request.form.get('company'),     # NEW
        "is_overdue": False
    }
    
    db.requests.insert_one(new_request)
    return redirect(url_for('dashboard.view_dashboard'))

@dashboard_bp.route('/api/request/delete/<request_id>', methods=['POST'])
def delete_request(request_id):
    """Deletes a maintenance request from the database."""
    if 'user' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    try:
        db.requests.delete_one({"_id": ObjectId(request_id)})
        return redirect(url_for('dashboard.view_dashboard'))
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@dashboard_bp.route('/api/request/save', methods=['POST'])
def save_request():
    """Unified route to either Add or Update a request."""
    if 'user' not in session:
        return redirect(url_for('auth.home'))
    
    # Get the ID from the form (it will be empty for NEW requests)
    req_id = request.form.get('request_id')
    eq_id = request.form.get('equipment')
    
    # Fetch equipment name for denormalized storage
    eq_obj = db.equipment.find_one({"_id": ObjectId(eq_id)}) if eq_id else None

    # Parse Scheduled Date
    sched_date_str = request.form.get('scheduled_date')
    sched_date = datetime.strptime(sched_date_str, "%Y-%m-%dT%H:%M") if sched_date_str else None

    data = {
        "subject": request.form.get('subject'),
        "equipment_id": ObjectId(eq_id) if eq_id else None,
        "equipment_name": eq_obj['name'] if eq_obj else "Unknown",
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

    if req_id:
        # UPDATE existing record
        db.requests.update_one({"_id": ObjectId(req_id)}, {"$set": data})
    else:
        # ADD new record
        data["employee"] = session['user']
        data["stage"] = "New Request"
        data["status_color"] = "grey"
        data["is_overdue"] = False
        db.requests.insert_one(data)

@dashboard_bp.route('/api/request/update', methods=['POST'])
def update_request():
    """Handles real-time updates for Auto-Saving notes, instructions, etc."""
    data = request.json
    db.requests.update_one({"_id": ObjectId(data['id'])}, {"$set": {data['field']: data['value']}})
    return jsonify({"success": True})