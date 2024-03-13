import logging
import random

from db.mongo import MongoDataBase
from entities.model import Model
from entities.observation import Observation
from model.representative import RepresentativeEstimator
from settings.model import ModelSettings
from training.mongo_trainer import MongoTrainer
from utils.resources import model_resource

logger = logging.getLogger(__name__)


def seed() -> None:
    db = MongoDataBase()
    observation_collection = db.get_collection(Observation.__name__.lower())
    model_collection = db.get_collection(Model.__name__.lower())
    cursor = observation_collection.find()
    results = list(cursor)

    if len(results) == 0:
        logger.info("Seeding database")

        seed_object = [
            dict(
                Observation(
                    feature_1=random.random(),
                    feature_2=random.random(),
                )
            )
            for _ in range(9)
        ]
        observation_collection.insert_many(seed_object)

        model_resource.run_trainer(
            trainer=MongoTrainer(
                client=db.get_client(),
                observation_collection=observation_collection,
                model_collection=model_collection,
            ),
            model=RepresentativeEstimator(model_settings=ModelSettings()),
        )

        logger.info("Seeding completed")
    else:
        logger.info("Seeding skipped")
