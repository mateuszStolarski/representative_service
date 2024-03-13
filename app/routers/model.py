import logging
from typing import Optional, Union

from entities.model import ModelStatus
from entities.observation import Observation
from fastapi import APIRouter, BackgroundTasks, Depends, Response, status
from model.representative import RepresentativeEstimator
from pymongo.collection import Collection
from settings.model import ModelSettings
from training.mongo_trainer import MongoTrainer
from utils.dependencies import (get_client_collection, get_model_collection,
                                get_observation_collection)
from utils.resources import model_resource

router = APIRouter(
    prefix="/model",
    tags=["model"],
    responses={404: {"description": "Not found"}},
)

logger = logging.getLogger(__name__)


@router.get(
    "/status",
    status_code=status.HTTP_200_OK,
)
async def model_status(
    response: Response,
    collection: Optional[Collection] = Depends(get_model_collection),
) -> Union[Response, dict]:
    try:
        in_training_status = collection.find(
            filter={
                "status": ModelStatus.in_training.name,
            }
        )
        current_model = collection.find_one(
            filter={
                "status": ModelStatus.in_usage.name,
            },
            projection={
                "_id": 0,
                "name": 1,
                "start_train_date": 1,
                "finish_train_date": 1,
                "k_nearest_neighbors": 1,
                "n_clusters": 1,
            },
        )
        in_training_status = list(in_training_status)

        return {
            "in_training": (
                None
                if len(in_training_status) == 0
                else [
                    {
                        "name": training_model["name"],
                        "start_train_date": training_model["start_train_date"],
                        "metadata": training_model["metadata"],
                    }
                    for training_model in in_training_status
                ]
            ),
            "current": current_model,
        }
    except Exception as ex:
        logger.exception(str(ex))
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    return response


@router.put(
    "/train",
    status_code=status.HTTP_200_OK,
)
async def train(
    response: Response,
    background_tasks: BackgroundTasks,
    additional_observations: Optional[list[Observation]] = None,
    client: Optional[Collection] = Depends(get_client_collection),
    observation_collection: Optional[Collection] = Depends(get_observation_collection),
    model_collection: Optional[Collection] = Depends(get_model_collection),
) -> Union[Response, dict]:
    try:
        model = RepresentativeEstimator(model_settings=ModelSettings())
        trainer = MongoTrainer(
            client=client,
            observation_collection=observation_collection,
            model_collection=model_collection,
        )
        background_tasks.add_task(
            model_resource.run_trainer,
            trainer,
            model,
            additional_observations,
        )
        return status.HTTP_200_OK
    except Exception as ex:
        logger.exception(str(ex))
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    return response


@router.post(
    "/predict",
    status_code=status.HTTP_200_OK,
)
async def predict(
    response: Response,
    item: Observation,
) -> Union[Response, dict]:
    try:
        return {"representative": model_resource.representative_model.predict(item)}
    except Exception as ex:
        logger.exception(str(ex))
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    return response
