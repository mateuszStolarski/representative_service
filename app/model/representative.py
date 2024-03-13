from __future__ import annotations

import math
from typing import Optional, Union

import numpy as np
from entities.model import Model, ModelStatus
from entities.observation import Observation
from model.base import BaseModel
from settings.model import ModelSettings


class RepresentativeCluster:
    def __init__(
        self,
        k_neares_neighbors: int,
        weights: Optional[list[Observation]] = None,
    ) -> None:
        self._k_nearest_neighbors = k_neares_neighbors
        self._weights = weights

    def fit(self, items: list[Observation]) -> None:
        self._weights = items

    def _calculate_distance(
        self,
        src: Observation,
        dst: Observation,
    ) -> float:
        return math.dist(src.as_point(), dst.as_point())

    def predict(self, item: Observation) -> float:
        distances = [
            self._calculate_distance(src=src, dst=item) for src in self._weights
        ]
        denominator = 1 + np.mean(sorted(distances)[: self._k_nearest_neighbors])
        return 1 / denominator

    def to_list(
        self,
    ) -> list[dict]:
        return [dict(item) for item in self._weights]

    @staticmethod
    def from_list(items: list[dict]) -> RepresentativeCluster:
        weights = [Observation(**item) for item in items]
        return RepresentativeCluster(
            k_neares_neighbors=len(weights),
            weights=weights,
        )


class RepresentativeEstimator(BaseModel):
    def __init__(
        self,
        model_settings: Optional[ModelSettings] = None,
        model_entity: Optional[Model] = None,
    ) -> None:
        self.name = "RepresentativeEstimator"
        if model_settings == None and model_entity == None:
            raise Exception(
                f"{self.name} require to pass either {ModelSettings.__name__} or {Model.__name__}"
            )

        self._k_nearest_neighbors = (
            model_entity.k_nearest_neighbors
            if model_entity
            else model_settings.k_nearest_neighbors
        )
        self._n_clusters = (
            model_entity.n_clusters if model_entity else model_settings.n_clusters
        )

        self._clusters: Union[list[RepresentativeCluster], None] = (
            [RepresentativeCluster.from_list(weight) for weight in model_entity.weights]
            if model_entity
            else None
        )
        super().__init__(
            status=model_entity.status if model_entity else None,
            start_train_date=model_entity.start_train_date if model_entity else None,
            finish_train_date=model_entity.finish_train_date if model_entity else None,
        )

    def to_entity(self) -> Model:
        if self._status == None:
            raise Exception("Parsing estimator to entity require training")

        return Model(
            name=self.name,
            status=self._status,
            start_train_date=self._start_train_date,
            finish_train_date=(
                self._finish_train_date if self._finish_train_date else None
            ),
            k_nearest_neighbors=self._k_nearest_neighbors,
            n_clusters=self._n_clusters,
            weights=(
                [cluster.to_list() for cluster in self._clusters]
                if self._clusters
                else None
            ),
        )

    def predict(self, item: Observation) -> float:
        if self._status != ModelStatus.in_usage.name:
            raise Exception("Only in_usage model can predict")

        return np.mean([cluster.predict(item) for cluster in self._clusters])

    def fit(self, items: list[Observation]) -> None:
        splitted_items = np.array_split(np.array(items), self._n_clusters)
        clusters = [
            RepresentativeCluster(self._k_nearest_neighbors)
            for _ in range(self._n_clusters)
        ]

        for item, cluster in zip(splitted_items, clusters):
            cluster.fit(item)

        self._clusters = clusters
