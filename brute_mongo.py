from pymongo import MongoClient
import sys

def try_conn(uri):
    try:
        client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        return True
    except Exception as e:
        print(f"FAILED: {e}")
        return False

# Variant: change the 'l' (ell) to 'I' (eye) or '1' (one)
passwords = [] # Cleared old passwords
pwd_from_env = os.environ.get('MONGODB_PASSWORD', '')
if pwd_from_env:
    passwords.append(pwd_from_env)

base_uri = "mongodb+srv://abhishekkurimeti97_db_user:{}@cluster0.gege15n.mongodb.net/parkisense?retryWrites=true&w=majority"

for p in passwords:
    u = base_uri.format(p)
    print(f"Trying password variation: {p}")
    if try_conn(u):
        print(f"SUCCESS! The correct password is: {p}")
        sys.exit(0)

print("No variation worked.")
