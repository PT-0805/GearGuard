from pymongo import MongoClient

# YOUR URI
MONGO_URI = "mongodb+srv://dbUserrr:MyPassisSafe@cluster0.ldlhqan.mongodb.net/?appName=Cluster0"

def get_db():
    client = MongoClient(MONGO_URI)
    # This creates/connects to a DB named 'user_system_db'
    return client.user_system_db