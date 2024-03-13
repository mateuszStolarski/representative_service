import os
from distutils.util import strtobool

from pydantic import BaseModel


class AppSettings(BaseModel):
    use_seed: bool = bool(
        strtobool(
            os.environ.get(
                "USE_SEED",
                "True",
            )
        )
    )
