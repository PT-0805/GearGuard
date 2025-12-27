from flask import Blueprint, session, redirect, url_for, render_template, request, jsonify
from database import get_db
from bson.objectid import ObjectId

pages_bp = Blueprint('pages', __name__)
db = get_db()

def check_login():
    return 'user' in session

@pages_bp.route('/equipment')
def equipment():
    if 'user' not in session: return redirect(url_for('auth.home'))
    
    # 1. Fetch Data for Tables
    equipment_list = list(db.equipment.find())
    catalog_list = list(db.equipment_categories.find())
    
    # 2. Fetch Data for Dropdowns
    teams = list(db.teams.find())
    users = list(db.users.find())
    work_centers = list(db.work_centers.find())
    
    # 3. Define the Company List (This was missing!)
    companies = [
        "My Company (San Francisco)", 
        "My Company (New York)", 
        "Global Logistics", 
        "Tech Hub HQ"
    ]

    return render_template('equipment.html', 
                           equipment=equipment_list,
                           catalogs=catalog_list,
                           teams=teams,
                           users=users,
                           work_centers=work_centers,
                           companies=companies, # <--- Added this
                           active_page='equipment')

# --- API FOR CATALOG SAVING ---
@pages_bp.route('/api/catalog/save', methods=['POST'])
def save_catalog():
    if 'user' not in session: return redirect(url_for('auth.home'))
    cat_id = request.form.get('cat_id')
    data = {
        "name": request.form.get('name'),
        "responsible": request.form.get('responsible'),
        "company": request.form.get('company')
    }
    if cat_id:
        db.equipment_categories.update_one({"_id": ObjectId(cat_id)}, {"$set": data})
    else:
        db.equipment_categories.insert_one(data)
    return redirect(url_for('pages.equipment'))

@pages_bp.route('/api/equipment/save', methods=['POST'])
def save_equipment():
    if 'user' not in session: return redirect(url_for('auth.home'))
    
    eq_id = request.form.get('eq_id')
    scrap_date = request.form.get('scrap_date')
    
    data = {
        "name": request.form.get('name'),
        "category": request.form.get('category'),
        "company": request.form.get('company'),
        "used_by_type": request.form.get('used_by_type'), # Employee | Location | Department
        "maintenance_team": request.form.get('maintenance_team'),
        "assigned_date": request.form.get('assigned_date'),
        "technician": request.form.get('technician'),
        "employee": request.form.get('employee'),
        "scrap_date": scrap_date,
        "location": request.form.get('location'),
        "work_center": request.form.get('work_center'),
        "description": request.form.get('description'),
        "status": "Scrapped" if scrap_date else "Active" # Logic: Scrap Date sets status
    }

    if eq_id and eq_id != "":
        db.equipment.update_one({"_id": ObjectId(eq_id)}, {"$set": data})
    else:
        db.equipment.insert_one(data)
        
    return redirect(url_for('pages.equipment'))
@pages_bp.route('/api/equipment/get/<eq_id>')
def get_single_equipment(eq_id):
    if 'user' not in session: return jsonify({"error": "Unauthorized"}), 401
    try:
        # Fetch data by ID
        item = db.equipment.find_one({"_id": ObjectId(eq_id)})
        if item:
            item['_id'] = str(item['_id'])
            return jsonify(item)
        return jsonify({"error": "Not found"}), 404
    except:
        return jsonify({"error": "Invalid ID"}), 400
    
# --- EQUIPMENT CATEGORY ROUTES ---

@pages_bp.route('/equipment-categories')
def equipment_categories():
    if 'user' not in session: return redirect(url_for('auth.home'))
    # Fetch all categories from the 'equipment_categories' collection
    categories = list(db.equipment_categories.find())
    return render_template('equipment_categories.html', categories=categories, active_page='equipment_categories')

@pages_bp.route('/api/equipment-categories/save', methods=['POST'])
def save_category():
    if 'user' not in session: return redirect(url_for('auth.home'))
    
    cat_id = request.form.get('cat_id')
    data = {
        "name": request.form.get('name'),
        "maintenance_team": request.form.get('maintenance_team'),
        "description": request.form.get('description')
    }

    if cat_id and cat_id != "":
        db.equipment_categories.update_one({"_id": ObjectId(cat_id)}, {"$set": data})
    else:
        db.equipment_categories.insert_one(data)
        
    return redirect(url_for('pages.equipment_categories'))

@pages_bp.route('/api/equipment-categories/<cat_id>')
def get_category_details(cat_id):
    if 'user' not in session: return jsonify({"error": "Unauthorized"}), 401
    category = db.equipment_categories.find_one({"_id": ObjectId(cat_id)})
    if category:
        category['_id'] = str(category['_id'])
        return jsonify(category)
    return jsonify({"error": "Not found"}), 404

@pages_bp.route('/kanban')
def kanban():
    if 'user' not in session: return redirect(url_for('auth.home'))
    
    # Fetch all requests
    all_reqs = list(db.requests.find())
    
    # Group requests by stage for the columns
    board = {
        "New Request": [r for r in all_reqs if r.get('stage') == "New Request"],
        "In Progress": [r for r in all_reqs if r.get('stage') == "In Progress"],
        "Done": [r for r in all_reqs if r.get('stage') == "Done"],
        "Scrap": [r for r in all_reqs if r.get('stage') == "Scrap"]
    }
    
    return render_template('kanban.html', board=board, active_page='kanban')

@pages_bp.route('/api/kanban/move', methods=['POST'])
def move_request():
    if 'user' not in session: return jsonify({"success": False}), 401
    
    data = request.json
    db.requests.update_one(
        {"_id": ObjectId(data['id'])},
        {"$set": {"stage": data['new_stage']}}
    )
    return jsonify({"success": True})

@pages_bp.route('/api/equipment-categories/delete/<cat_id>', methods=['POST'])
def delete_category(cat_id):
    if 'user' not in session: return jsonify({"error": "Unauthorized"}), 401
    db.equipment_categories.delete_one({"_id": ObjectId(cat_id)})
    return redirect(url_for('pages.equipment_categories'))

@pages_bp.route('/api/equipment-categories/quick-add', methods=['POST'])
def quick_add_category():
    if 'user' not in session: return jsonify({"error": "Unauthorized"}), 401
    
    data = {
        "name": request.json.get('name'),
        "maintenance_team": "Internal Maintenance", # Default for quick add
        "description": "Quickly added via Equipment form"
    }
    
    # Avoid duplicates
    existing = db.equipment_categories.find_one({"name": data['name']})
    if not existing:
        new_id = db.equipment_categories.insert_one(data).inserted_id
        return jsonify({"success": True, "id": str(new_id), "name": data['name']})
    
    return jsonify({"success": False, "error": "Category already exists"})


@pages_bp.route('/calendar')
def calendar():
    if 'user' not in session: return redirect(url_for('auth.home'))
    return render_template('calendar.html', active_page='calendar')

# API for the Calendar to fetch events
@pages_bp.route('/api/calendar/events')
def get_calendar_events():
    if 'user' not in session: return jsonify([]), 401
    
    # Fetch all requests that have a scheduled date
    requests = list(db.requests.find({"scheduled_date": {"$ne": None}}))
    events = []

    for req in requests:
        # Determine color based on status_color or type
        color = '#007bff' # Default Blue
        if req.get('status_color') == 'red': color = '#ff3b30' # Apple Red
        elif req.get('status_color') == 'green': color = '#34c759' # Apple Green
        elif req.get('type') == 'Preventive': color = '#5856d6' # Apple Purple

        events.append({
            "id": str(req['_id']),
            "title": f"{req.get('subject')} ({req.get('equipment_name')})",
            "start": req['scheduled_date'].isoformat(),
            "backgroundColor": color,
            "borderColor": color,
            "extendedProps": {
                "technician": req.get('technician', 'Unassigned'),
                "type": req.get('type', 'Corrective')
            }
        })
    
    return jsonify(events)

@pages_bp.route('/teams')
def teams():
    if 'user' not in session: return redirect(url_for('auth.home'))
    
    teams_list = list(db.teams.find())
    return render_template('teams.html', teams=teams_list, active_page='teams')

@pages_bp.route('/api/teams/save', methods=['POST'])
def save_team():
    if 'user' not in session: return redirect(url_for('auth.home'))
    
    team_id = request.form.get('team_id')
    # Filter out empty member names from the dynamic list
    members = [m for m in request.form.getlist('members[]') if m.strip()]
    
    data = {
        "name": request.form.get('name'),
        "company": request.form.get('company'),
        "members": members
    }

    if team_id:
        db.teams.update_one({"_id": ObjectId(team_id)}, {"$set": data})
    else:
        db.teams.insert_one(data)
        
    return redirect(url_for('pages.teams'))

@pages_bp.route('/api/teams/<team_id>')
def get_team_details(team_id):
    team = db.teams.find_one({"_id": ObjectId(team_id)})
    if team:
        team['_id'] = str(team['_id'])
        return jsonify(team)
    return jsonify({"error": "Not found"}), 404

# NEW: API to Add Equipment
@pages_bp.route('/api/equipment/add', methods=['POST'])
def add_equipment():
    if not check_login(): return redirect(url_for('auth.home'))
    
    # Get form data
    data = {
        "name": request.form.get('name'),
        "serial_number": request.form.get('serial_number'),
        "category": request.form.get('category'),
        "department": request.form.get('department'),
        "company": request.form.get('company'),
        "employee_owner": request.form.get('employee'),  # The person who uses it
        "technician_name": request.form.get('technician'), # Assigned maintainer
        "health": 100,      # Default new item health
        "status": "Good"    # Default status
    }
    
    db.equipment.insert_one(data)
    
    # Redirect back to the equipment page to see the new item
    return redirect(url_for('pages.equipment'))

@pages_bp.route('/api/teams/delete/<team_id>', methods=['POST'])
def delete_team(team_id):
    if 'user' not in session: return jsonify({"error": "Unauthorized"}), 401
    try:
        db.teams.delete_one({"_id": ObjectId(team_id)})
        return redirect(url_for('pages.teams'))
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
@pages_bp.route('/work-centers')
def work_centers():
    if 'user' not in session: return redirect(url_for('auth.home'))
    # Fetch all work centers from the 'work_centers' collection
    wc_list = list(db.work_centers.find())
    return render_template('work_centers.html', work_centers=wc_list, active_page='work_centers')

@pages_bp.route('/api/work-centers/save', methods=['POST'])
def save_work_center():
    if 'user' not in session: return redirect(url_for('auth.home'))
    
    wc_id = request.form.get('wc_id')
    data = {
        "name": request.form.get('name'),
        "code": request.form.get('code'),
        "tag": request.form.get('tag'),
        "alt_wc": request.form.get('alt_wc'),
        "cost_per_hour": request.form.get('cost_per_hour'),
        "capacity": request.form.get('capacity'),
        "time_efficiency": request.form.get('time_efficiency'),
        "oee_target": request.form.get('oee_target')
    }

    if wc_id and wc_id != "":
        db.work_centers.update_one({"_id": ObjectId(wc_id)}, {"$set": data})
    else:
        db.work_centers.insert_one(data)
        
    return redirect(url_for('pages.work_centers'))

@pages_bp.route('/api/work-centers/<wc_id>')
def get_wc_details(wc_id):
    if 'user' not in session: return jsonify({"error": "Unauthorized"}), 401
    wc = db.work_centers.find_one({"_id": ObjectId(wc_id)})
    if wc:
        wc['_id'] = str(wc['_id'])
        return jsonify(wc)
    return jsonify({"error": "Not found"}), 404

@pages_bp.route('/api/work-centers/delete/<wc_id>', methods=['POST'])
def delete_work_center(wc_id):
    if 'user' not in session: return jsonify({"error": "Unauthorized"}), 401
    db.work_centers.delete_one({"_id": ObjectId(wc_id)})
    return redirect(url_for('pages.work_centers'))