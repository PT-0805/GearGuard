from database import get_db
from bson.objectid import ObjectId
from datetime import datetime

db = get_db()

def create_perfect_test():
    # 1. Define a specific ID so we can find it easily later
    test_id = ObjectId("650000000000000000000001")
    
    # 2. Delete it if it exists (so we can run this script multiple times)
    db.requests.delete_one({"_id": test_id})

    # 3. Insert the "Perfect" Record
    db.requests.insert_one({
        "_id": test_id,
        "subject": "Test - Conveyor Belt Jam",
        "employee": "Mitchell Admin",
        "equipment_name": "Conveyor Belt 05",
        "category": "Machinery",
        "type": "Corrective",
        "stage": "In Progress",
        
        # New Fields for your functionality
        "status_state": "in_progress",  # Options: in_progress (Gray), ready (Green), blocked (Red)
        "notes": "Initial technician notes: The belt seems to be misaligned...",
        
        "technician": "Aka Foster",
        "scheduled_date": datetime.now(),
        "duration": "02:30",
        "company": "My Company",
        "is_overdue": False
    })

    print(f"✅ Created Test Product with ID: {test_id}")
    print("Refresh your Dashboard to see 'Test - Conveyor Belt Jam'")

if __name__ == "__main__":
    create_perfect_test()