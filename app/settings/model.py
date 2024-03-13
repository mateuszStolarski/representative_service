import os

from pydantic import BaseModel


class ModelSettings(BaseModel):
    k_nearest_neighbors: int = int(os.environ.get("K_NEAREST_NEIGHBORS"))
    n_clusters: int = int(os.environ.get("N_CLUSTERS"))
