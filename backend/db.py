from pymongo import MongoClient
import os
import copy

MONGO_URL = os.getenv("MONGO_URL", "mongodb://127.0.0.1:27017")
client = MongoClient(MONGO_URL, serverSelectionTimeoutMS=1000)

try:
    # Attempt to ping the database
    client.admin.command('ping')
    USE_MONGO = True
except Exception:
    USE_MONGO = False

class MockCollection:
    """An in-memory fallback collection that mocks basic MongoDB operations."""
    def __init__(self):
        self._data = []
        
    def insert_one(self, doc):
        d = copy.deepcopy(doc)
        if "_id" not in d:
            d["_id"] = len(self._data) + 1
        self._data.append(d)
        
    def find_one(self, query):
        for d in self._data:
            match = True
            for k, v in query.items():
                if d.get(k) != v:
                    match = False
                    break
            if match:
                return copy.deepcopy(d)
        return None
        
    def find(self, query=None, projection=None):
        query = query or {}
        results = []
        for d in self._data:
            match = True
            for k, v in query.items():
                if d.get(k) != v:
                    match = False
                    break
            if match:
                res = copy.deepcopy(d)
                if projection and "_id" in projection and projection["_id"] == 0:
                    res.pop("_id", None)
                results.append(res)
        return results
        
    def count_documents(self, query):
        return len(self.find(query))
        
    def update_many(self, query, update):
        for d in self._data:
            match = True
            for k, v in query.items():
                if d.get(k) != v:
                    match = False
                    break
            if match:
                if "$max" in update:
                    for k, v in update["$max"].items():
                        d[k] = max(d.get(k, 0), v)
                if "$set" in update:
                    for k, v in update["$set"].items():
                        d[k] = v

if USE_MONGO:
    db = client["assignment_system"]
    submissions_collection = db["submissions"]
    assignments_collection = db["assignments"]
    users_collection = db["users"]
    notifications_collection = db["notifications"]
    certificates_collection = db["certificates"]
else:
    print("WARNING: MongoDB not found locally. Falling back to in-memory storage.")
    submissions_collection = MockCollection()
    assignments_collection = MockCollection()
    users_collection = MockCollection()
    notifications_collection = MockCollection()
    certificates_collection = MockCollection()
