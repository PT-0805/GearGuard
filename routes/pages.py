from flask import Blueprint, session, redirect, url_for, render_template
from database import get_db

pages_bp = Blueprint('pages', __name__)
db = get_db()

def check_login():
    return 'user' in session

@pages_bp.route('/equipment')
def equipment():
    if not check_login(): return redirect(url_for('auth.home'))
    
    # FETCH REAL DATA
    equipment_list = list(db.equipment.find())
    
    # We render a new template (code below)
    return render_template('equipment.html', 
                           equipment=equipment_list, 
                           active_page='equipment')

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