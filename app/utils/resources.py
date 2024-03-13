from typing import Optional

from entities.model import Model, ModelStatus
from entities.observation import Observation
from model.representative import RepresentativeEstimator
from settings.model import ModelSettings
from training.mongo_trainer import MongoTrainer
from utils.dependencies import get_model_collection


class ModelResource:
    def __init__(self) -> None:
        self.representative_model = self._get_model()

    def run_trainer(
        self,
        trainer: MongoTrainer,
        model: RepresentativeEstimator,
        additional_observations: Optional[list[Observation]] = None,
    ) -> None:
        trainer.fit(
            model=model,
            additional_observations=additional_observations,
        )

        self.update()

    def update(self) -> None:
        self.representative_model = self._get_model()

    def _get_model(self):
        model_collection = get_model_collection()
        model_entity = model_collection.find_one(
            filter={"status": ModelStatus.in_usage.name}
        )
        return (
            RepresentativeEstimator(model_entity=Model(**model_entity))
            if model_entity
            else RepresentativeEstimator(model_settings=ModelSettings())
        )


model_resource = ModelResource()
