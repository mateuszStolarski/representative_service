from typing import Optional

from db.mongo import MongoDataBase
from pymongo import MongoClient
from pymongo.collection import Collection


def get_model_collection() -> Optional[Collection]:
    return MongoDataBase().get_collection("model")


def get_observation_collection() -> Optional[Collection]:
    return MongoDataBase().get_collection("observation")


def get_client_collection() -> Optional[MongoClient]:
    return MongoDataBase().get_client()
