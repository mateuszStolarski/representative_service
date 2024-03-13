import logging
from typing import Optional

from entities.observation import Observation
from fastapi import APIRouter, Depends, Response, status
from pymongo.collection import Collection
from utils.dependencies import get_observation_collection

router = APIRouter(
    prefix="/observation",
    tags=["observation"],
    responses={404: {"description": "Not found"}},
)

logger = logging.getLogger(__name__)


@router.post(
    "/one/new",
    status_code=status.HTTP_201_CREATED,
)
async def new_observation(
    item: Observation,
    response: Response,
    collection: Optional[Collection] = Depends(get_observation_collection),
) -> Response:
    try:
        collection.insert_one(dict(item))
        response.status_code = status.HTTP_201_CREATED
    except Exception as ex:
        logger.exception(str(ex))
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    return response


@router.post(
    "/many/new",
    status_code=status.HTTP_201_CREATED,
)
async def new_observations(
    items: list[Observation],
    response: Response,
    collection: Optional[Collection] = Depends(get_observation_collection),
) -> Response:
    try:
        collection.insert_many([dict(item) for item in items])
        response.status_code = status.HTTP_201_CREATED
    except Exception as ex:
        logger.exception(str(ex))
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    return response
