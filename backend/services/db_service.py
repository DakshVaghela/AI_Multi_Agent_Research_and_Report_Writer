from datetime import datetime
from typing import Any, Dict, Optional
import pymongo
from backend.config.settings import settings


class DatabaseService:
    """
    Service for interacting with MongoDB.
    """

    def __init__(self):
        self.client = pymongo.MongoClient(settings.MONGO_URI)
        self.db = self.client[settings.MONGO_DB]
        # Ensure email index is unique at database level
        self.db.users.create_index("email", unique=True)

    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a user document by email.
        """
        return self.db.users.find_one({"email": email.lower().strip()})

    def create_user(self, email: str, hashed_password: str, name: str = None) -> Dict[str, Any]:
        """
        Create a new user document in the database.
        """
        user_doc = {
            "email": email.lower().strip(),
            "password": hashed_password,
            "name": name.strip() if name else "",
            "created_at": datetime.utcnow(),
        }
        self.db.users.insert_one(user_doc)
        return user_doc


# Lazy-loaded database service singleton instance
class LazyDatabaseService:
    def __init__(self):
        self._service: DatabaseService | None = None

    def _get_service(self) -> DatabaseService:
        if self._service is None:
            self._service = DatabaseService()
        return self._service

    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        return self._get_service().get_user_by_email(email)

    def create_user(self, email: str, hashed_password: str, name: str = None) -> Dict[str, Any]:
        return self._get_service().create_user(email, hashed_password, name)


db_service = LazyDatabaseService()
