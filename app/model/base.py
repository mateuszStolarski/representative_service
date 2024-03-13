from __future__ import annotations

from abc import abstractmethod
from datetime import datetime
from typing import Literal, Optional

from entities.model import Model
from entities.observation import Observation


class BaseModel:
    def __init__(
        self,
        status: Optional[Literal["in_training", "in_usage", "archived"]],
        start_train_date: Optional[datetime],
        finish_train_date: Optional[datetime],
    ) -> None:
        self._status = status
        self._start_train_date = start_train_date
        self._finish_train_date = finish_train_date

    @property
    def status(self) -> Literal["in_training", "in_usage", "archived"]:
        return self._status

    @status.setter
    def status(self, var: Literal["in_training", "in_usage", "archived"]) -> None:
        self._status = var

    @property
    def start_train_date(self) -> datetime:
        return self._start_train_date

    @start_train_date.setter
    def start_train_date(self, var: datetime) -> None:
        self._start_train_date = var

    @property
    def finish_train_date(self) -> datetime:
        return self._finish_train_date

    @finish_train_date.setter
    def finish_train_date(self, var: datetime) -> None:
        self._finish_train_date = var

    @abstractmethod
    def to_entity(self) -> Model:
        pass

    @abstractmethod
    def fit(self, items: list[Observation]):
        pass

    @abstractmethod
    def predict(self, item: Observation):
        pass
