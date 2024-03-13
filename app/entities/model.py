from datetime import datetime
from enum import Enum
from typing import Any, Literal, Optional

from pydantic import BaseModel


class ModelStatus(Enum):
    in_training = 1
    in_usage = 2
    archived = 3


class Model(BaseModel):
    name: str
    status: Literal["in_training", "in_usage", "archived"]
    start_train_date: datetime
    finish_train_date: Optional[datetime]
    k_nearest_neighbors: int
    n_clusters: int
    weights: Optional[list[list[dict]]]
    metadata: Optional[dict[str, Any]]
