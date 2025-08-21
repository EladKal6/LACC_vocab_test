from datetime import datetime
from pymongo import MongoClient

class MongoService:
    def __init__(self, mongo_uri, db_name, collection_name):
        self.client = MongoClient(mongo_uri)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]

    def record_session(self, user_id: str, question_results: list, score: int):
        session_doc = {
            'user_id': user_id,
            'timestamp': datetime.utcnow(),
            'questions': question_results,
            'score': score,
            'total': len(question_results)
        }
        result = self.collection.insert_one(session_doc)
        return result.inserted_id

    def get_recent_sessions(self, limit: int = 10):
        cursor = self.collection.find().sort('timestamp', -1).limit(limit)
        return list(cursor) 