from pymongo import MongoClient
import sys

def try_conn(pwd):
    uri = f"mongodb+srv://abhishekkurimeti97_db_user:{pwd}@cluster0.gege15n.mongodb.net/parkisense?retryWrites=true&w=majority"
    try:
        client = MongoClient(uri, serverSelectionTimeoutMS=2000)
        client.admin.command('ping')
        return True
    except Exception as e:
        # print(f"PWD: {pwd} - FAILED: {e}")
        return False

base_pwd = os.environ.get('MONGODB_BASE_PASSWORD', 'E1lOIPImeOw43Izw')
passwords = [base_pwd] # Testing current configured password only
# Add suspects manually if needed from environment
if os.environ.get('MONGODB_SUSPECT'):
    passwords.append(os.environ.get('MONGODB_SUSPECT'))

for p in passwords:
    print(f"Testing specifically: {p}")
    if try_conn(p):
        print(f"🎉 FOUND! The correct password is: {p}")
        sys.exit(0)

print("None of the common image suspects worked.")
