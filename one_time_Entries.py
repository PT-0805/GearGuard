from database import get_db
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta

db = get_db()

def seed():
    print("⚠️  Clearing old data...")
    db.users.delete_many({})
    db.teams.delete_many({})       # NEW
    db.equipment.delete_many({})
    db.requests.delete_many({})

    # 1. CREATE TEAMS (Per your Overview: Mechanics, Electricians, IT)
    print("🌱 Seeding Teams...")
    mechanics_id = db.teams.insert_one({"name": "Mechanics"}).inserted_id
    electricians_id = db.teams.insert_one({"name": "Electricians"}).inserted_id
    it_id = db.teams.insert_one({"name": "IT Support"}).inserted_id

    # 2. CREATE USERS & TECHNICIANS
    print("🌱 Seeding Users...")
    db.users.insert_one({
        "name": "Mitchell Admin",
        "email": "admin@test.com",
        "password": generate_password_hash("1234"),
        "role": "Manager"
    })
    
    # Technicians linked to teams
    tech_1 = db.users.insert_one({"name": "Aka Foster", "email": "aka@test.com", "password": generate_password_hash("1234"), "role": "Technician", "team_id": mechanics_id}).inserted_id
    tech_2 = db.users.insert_one({"name": "Bob Smith", "email": "bob@test.com", "password": generate_password_hash("1234"), "role": "Technician", "team_id": electricians_id}).inserted_id

    # 3. CREATE EQUIPMENT (With Serial No, Location, Department)
    print("🌱 Seeding Equipment...")
    gen_a_id = db.equipment.insert_one({
        "name": "Generator A",
        "serial_number": "GEN-2024-001",
        "category": "Machinery",
        "department": "Production",
        "location": "Warehouse Zone 1",
        "maintenance_team_id": mechanics_id, # Assigned to Mechanics
        "health": 20, # Critical
        "status": "Active"
    }).inserted_id

    printer_id = db.equipment.insert_one({
        "name": "HP Printer 01",
        "serial_number": "PRT-9988-X",
        "category": "Electronics",
        "department": "Office",
        "location": "HQ - Floor 2",
        "maintenance_team_id": it_id, # Assigned to IT
        "health": 90, 
        "status": "Active"
    }).inserted_id

    # 4. CREATE REQUESTS (Corrective vs Preventive)
    print("🌱 Seeding Requests...")
    db.requests.insert_many([
        {
            "subject": "Leaking Oil",
            "type": "Corrective", # Breakdown
            "equipment_id": gen_a_id,
            "equipment_name": "Generator A", # De-normalized for easy display
            "technician_id": tech_1,
            "stage": "New", # New | In Progress | Repaired | Scrap
            "scheduled_date": datetime.now(),
            "duration": 0,
            "is_overdue": True
        },
        {
            "subject": "Routine Checkup",
            "type": "Preventive", # Scheduled
            "equipment_id": printer_id,
            "equipment_name": "HP Printer 01",
            "technician_id": None, # Unassigned
            "stage": "New",
            "scheduled_date": datetime.now() + timedelta(days=7), # Next week
            "duration": 0,
            "is_overdue": False
        }
    ])

    print("✅ Database populated with Project Outline Schema!")

if __name__ == "__main__":
    seed()