from pymongo import MongoClient
import sys

def try_conn(uri):
    try:
        client = MongoClient(uri, serverSelectionTimeoutMS=2000)
        client.admin.command('ping')
        return True
    except Exception:
        return False

base_pwd = os.environ.get('MONGODB_BASE_PASSWORD', 'E1lOIPImeOw43Izw')
# Testing variations for first 4 characters
chars1 = ['l', 'I', '1'] 
chars2 = ['O', '0']

for c1 in chars1:
    for c2 in chars2:
        # Build the password variation
        var_pwd = f"E1{c1}{c2}" + base_pwd[4:]
        print(f"Trying: {var_pwd[:5]}...")
        u = f"mongodb+srv://abhishekkurimeti97_db_user:{var_pwd}@cluster0.gege15n.mongodb.net/parkisense?retryWrites=true&w=majority"
        if try_conn(u):
            print(f"SUCCESS! Found working credentials.")
            sys.exit(0)

print("No variation found.")
