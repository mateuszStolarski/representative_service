import logging
import time
from datetime import datetime
from typing import Optional

from entities.model import ModelStatus
from entities.observation import Observation
from model.base import BaseModel
from pymongo import MongoClient
from pymongo.collection import Collection

logger = logging.getLogger(__name__)


class MongoTrainer:
    def __init__(
        self,
        client: MongoClient,
        observation_collection: Collection,
        model_collection: Collection,
    ) -> None:
        self._client = client
        self._observation_collection = observation_collection
        self._model_collection = model_collection

    def _save_interruption(
        self,
        model: BaseModel,
        error: str,
        time: datetime,
    ) -> None:
        entity = model.to_entity()
        self._model_collection.update_one(
            filter={"status": ModelStatus.in_training.name},
            update={
                "$set": {
                    "name": entity.name,
                    "start_train_date": entity.start_train_date,
                    "k_nearest_neighbors": entity.k_nearest_neighbors,
                    "n_clusters": entity.n_clusters,
                    "metadata": {"exception": error, "time": time},
                }
            },
            upsert=True,
        )

    def _save_model(self, model: BaseModel) -> None:
        if model.status == ModelStatus.in_training.name:
            self._model_collection.insert_one(dict(model.to_entity()))
        if model.status == ModelStatus.in_usage.name:
            entity = model.to_entity()
            self._model_collection.update_many(
                filter={"status": ModelStatus.in_usage.name},
                update={"$set": {"status": ModelStatus.archived.name}},
            )
            self._model_collection.update_one(
                filter={"status": ModelStatus.in_training.name},
                update={
                    "$set": {
                        "finish_train_date": entity.finish_train_date,
                        "weights": entity.weights,
                        "status": entity.status,
                    }
                },
            )

    def _get_observations(self) -> list[Observation]:
        cursor = self._observation_collection.find()
        return [Observation(**item) for item in cursor]

    def fit(
        self,
        model: BaseModel,
        additional_observations: Optional[list[Observation]] = None,
    ) -> BaseModel:
        logger.info("Training started")
        model.start_train_date = datetime.now()
        model.status = ModelStatus.in_training.name
        try:
            self._save_model(model)

            observations = self._get_observations()
            if additional_observations:
                observations.extend(additional_observations)
            model.fit(observations)
            time.sleep(10)

            model.finish_train_date = datetime.now()
            model.status = ModelStatus.in_usage.name

            self._save_model(model)
            logger.info("Training completed")
        except Exception as ex:
            self._save_interruption(
                model=model,
                error=str(ex),
                time=datetime.now(),
            )
