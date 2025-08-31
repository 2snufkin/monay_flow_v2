"""
Database Configuration and Connection Management

This module handles database connections and connection pooling
for MongoDB databases only.
"""

import logging
from typing import Optional, Dict, Any
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection

from config.settings import get_settings

logger = logging.getLogger(__name__)


class MongoDBManager:
    """Manages MongoDB connections and operations."""

    def __init__(self):
        """Initialize MongoDB manager."""
        self.settings = get_settings()
        self._client: Optional[MongoClient] = None
        self._database: Optional[Database] = None

    def get_client(self) -> MongoClient:
        """
        Get MongoDB client connection.

        Returns:
            MongoClient: MongoDB client instance
        """
        if not self._client:
            mongo_url = self.settings.database.mongo_url
            if not mongo_url:
                raise ValueError("MongoDB URL not configured")

            self._client = MongoClient(mongo_url)

        return self._client

    def get_database(self, database_name: str) -> Database:
        """
        Get MongoDB database instance.

        Args:
            database_name: Name of the database

        Returns:
            Database: MongoDB database instance
        """
        if not self._database or self._database.name != database_name:
            client = self.get_client()
            self._database = client[database_name]

        return self._database

    def get_collection(self, database_name: str, collection_name: str) -> Collection:
        """
        Get MongoDB collection instance.

        Args:
            database_name: Name of the database
            collection_name: Name of the collection

        Returns:
            Collection: MongoDB collection instance
        """
        db = self.get_database(database_name)
        return db[collection_name]

    def close(self):
        """Close the MongoDB connection."""
        if self._client:
            self._client.close()
            self._client = None
            self._database = None


# Connection functions for backward compatibility
def get_mongo_client() -> MongoClient:
    """
    Get MongoDB client connection.

    Returns:
        MongoClient: MongoDB client instance
    """
    manager = MongoDBManager()
    return manager.get_client()


def get_mongo_database(database_name: str) -> Database:
    """
    Get MongoDB database instance.

    Returns:
        Database: MongoDB database instance
    """
    manager = MongoDBManager()
    return manager.get_database(database_name)


def get_mongo_collection(database_name: str, collection_name: str) -> Collection:
    """
    Get MongoDB collection instance.

    Returns:
        Collection: MongoDB collection instance
    """
    manager = MongoDBManager()
    return manager.get_collection(database_name, collection_name)
