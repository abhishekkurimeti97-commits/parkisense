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

# Base: E1lOIPlmeOw43Izw (Length 16)
# Straight Line positions:
# 2: l/I/1
# 4: I/l/1
# 6: l/I/1
# 13: I/l/1

options = ['l', 'I', '1']
indices = [2, 4, 6, 13]
base_raw = os.environ.get('MONGODB_BASE_PASSWORD', 'E1lOIPlmeOw43Izw')
base = list(base_raw)

combinations = list(itertools.product(options, repeat=len(indices)))

print(f"Testing {len(combinations)} line variations...")

for combo in combinations:
    p = list(base)
    for i, char in enumerate(combo):
        p[indices[i]] = char
    pwd = "".join(p)
    if try_conn(pwd):
        print(f"🎉 SUCCESS! Found: {pwd}")
        sys.exit(0)

print("No line variation worked.")
