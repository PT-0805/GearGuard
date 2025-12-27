from flask import Blueprint, session, redirect, url_for, render_template, request, jsonify
from database import get_db

pages_bp = Blueprint('pages', __name__)
db = get_db()

def check_login():
    return 'user' in session

@pages_bp.route('/equipment')
def equipment():
    if not check_login(): return redirect(url_for('auth.home'))
    
    # 1. Handle Search Query
    query = request.args.get('q', '')
    search_filter = {}
    if query:
        # Search by name or serial number (case-insensitive)
        search_filter = {
            "$or": [
                {"name": {"$regex": query, "$options": "i"}},
                {"serial_number": {"$regex": query, "$options": "i"}}
            ]
        }

    # 2. Fetch Data
    equipment_list = list(db.equipment.find(search_filter))
    
    # Fetch technicians for the dropdown in the "New Equipment" modal
    # Assuming technicians have role="Technician" or belong to a team
    # For now, we just fetch all users to keep it simple, or filter if you have roles
    technicians = list(db.users.find()) 

    return render_template('equipment.html', 
                           equipment=equipment_list, 
                           technicians=technicians,
                           active_page='equipment')

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

@pages_bp.route('/teams')
def teams():
    if not check_login(): return redirect(url_for('auth.home'))
    
    teams_list = list(db.teams.find())
    return render_template('teams.html', 
                           teams=teams_list, 
                           active_page='teams')

@pages_bp.route('/calendar')
def calendar():
    if not check_login(): return redirect(url_for('auth.home'))
    
    # Fetch only Preventive maintenance for the calendar (as per outline)
    preventive_reqs = list(db.requests.find({"type": "Preventive"}))
    
    return render_template('calendar.html', 
                           requests=preventive_reqs, 
                           active_page='calendar')