from pydantic import BaseModel


class Observation(BaseModel):
    feature_1: float
    feature_2: float

    def as_point(self) -> list[float]:
        return [self.feature_1, self.feature_2]
