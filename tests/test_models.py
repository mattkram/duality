from typing import Type

import pytest

from duality.dtdl import Interface
from duality.models import BaseModel


class MyModel(BaseModel, model_prefix="duality", model_version=2):
    my_property: str


class MyChildModel(MyModel, model_prefix="duality:child", model_version=1):
    my_other_property: str


@pytest.mark.parametrize(
    "model_class, expected_id",
    [
        (MyModel, "dtmi:duality:my_model;2"),
        (MyChildModel, "dtmi:duality:child:my_child_model;1"),
    ],
)
def test_model_class_id(model_class: Type[BaseModel], expected_id: str) -> None:
    assert model_class.id == expected_id


def test_model_class_to_dtdl() -> None:
    assert MyModel.to_interface() == Interface(
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


def test_child_model_to_dtdl() -> None:
    assert MyChildModel.to_interface() == Interface(
        id="dtmi:duality:child:my_child_model;1",
        contents=[
            {
                "@type": "Property",
                "name": "my_other_property",
                "schema": "string",
            },
        ],
        extends="dtmi:duality:my_model;2",
        displayName="MyChildModel",
    )
