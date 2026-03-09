from pymongo import MongoClient
import itertools
import sys

def try_conn(pwd):
    uri = f"mongodb+srv://abhishekkurimeti97_db_user:{pwd}@cluster0.gege15n.mongodb.net/parkisense?retryWrites=true&w=majority"
    try:
        client = MongoClient(uri, serverSelectionTimeoutMS=1000)
        client.admin.command('ping')
        return True
    except Exception:
        return False

variants = {
    # index: [options]
    2: ['l', 'I', '1'],
    3: ['O', '0'],
    4: ['I', 'l', '1'],
    6: ['I', 'l', '1'],
    9: ['O', '0'],
    13: ['I', 'l', '1'],
}

base_raw = os.environ.get('MONGODB_BASE_PASSWORD', 'E1lOIPImeOw43Izw')
base = list(base_raw)
keys = sorted(variants.keys())
combinations = list(itertools.product(*[variants[k] for k in keys]))

print(f"Trying {len(combinations)} password variations...")

for combo in combinations:
    p_list = list(base)
    for i, char in enumerate(combo):
        p_list[keys[i]] = char
    pwd = "".join(p_list)
    if try_conn(pwd):
        print(f"SUCCESS! The correct password is: {pwd}")
        sys.exit(0)

print("No variation worked.")
