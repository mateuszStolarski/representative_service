from pymongo import MongoClient
from pymongo.collection import Collection
from settings.mongo import MongoSettings


class MongoDataBase:
    instance = None
    _settings = MongoSettings()

    def __new__(cls):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
            cls.instance.client = MongoClient(cls._settings.connection_string)
            cls.instance.database = cls.instance.client["representative"]

        return cls.instance

    def get_collection(self, name: str) -> Collection:
        return self.instance.database[name]

    def get_client(self) -> MongoClient:
        return self.instance.client
