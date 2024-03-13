from pydantic import BaseModel


class Observation(BaseModel):
    feature_1: float
    feature_2: float
