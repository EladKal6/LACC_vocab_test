from datetime import datetime
from .mongo_service import MongoService

class UserAnswerLog:
    """
    Interface for recording and retrieving user quiz sessions.
    Delegates all DB operations to MongoService.
    """
    def __init__(self, mongo_uri, db_name, collection_name):
        self.service = MongoService(mongo_uri, db_name, collection_name)

    def record_session(self, user_id: str, question_results: list, score: int):
        return self.service.record_session(user_id, question_results, score)

    def get_recent_sessions(self, limit: int = 10):
        return self.service.get_recent_sessions(limit)