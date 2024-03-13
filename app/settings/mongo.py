import os

from pydantic import BaseModel, SecretStr


class MongoSettings(BaseModel):
    connection_string: SecretStr = os.environ.get("CONNECTION_STRING")
