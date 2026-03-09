import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()
uri = os.environ.get('MONGODB_URI')
print(f"Testing URI: {uri}")

try:
    client = MongoClient(uri, serverSelectionTimeoutMS=5000)
    print("Connecting...")
    client.admin.command('ping')
    print("SUCCESS")
except Exception as e:
    print(f"ERROR TYPE: {type(e).__name__}")
    print(f"ERROR MESSAGE: {e}")
