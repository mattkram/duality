from typing import Generator
from typing import Type

import pytest

from duality.dtdl import Interface
from duality.models import BaseModel


@pytest.fixture()
def model_class() -> Generator[Type[BaseModel], None, None]:
    """Create a new model class"""

    class MyModel(BaseModel, model_prefix="duality", model_version=2):
        my_property: str

    yield MyModel


def test_model_class_id(model_class: Type[BaseModel]) -> None:
    assert model_class.id == "dtmi:duality:my_model;2"


def test_model_class_to_dtdl(model_class: Type[BaseModel]) -> None:
    assert model_class.to_interface() == Interface(
        id="dtmi:duality:my_model;2",
        contents=[
            {
                "@type": "Property",
                "name": "my_property",
                "schema": "string",
            }
        ],
        displayName="MyModel",
    )
