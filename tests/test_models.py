from typing import Generator
from typing import Type

import pytest

from duality.models import BaseModel


@pytest.fixture()
def model_class() -> Generator[Type[BaseModel], None, None]:
    """Create a new model class"""

    class MyModel(BaseModel, model_prefix="duality", model_version=2):
        my_property: str

    yield MyModel


def test_model_class_id(model_class):
    assert model_class.id == "dtmi:duality:my_model;2"
