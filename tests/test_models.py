import datetime
from typing import Type

import pytest

from duality.dtdl import Interface
from duality.models import BaseModel
from duality.models import Relationship


class MyModel(BaseModel, model_prefix="duality", model_version=2):
    my_parent_property: str


class MyChildModel(MyModel, model_prefix="duality:child", model_version=1):
    my_string_property: str
    my_int_property: int
    my_float_property: float
    my_bool_property: bool
    my_date_property: datetime.date
    my_datetime_property: datetime.datetime
    my_time_property: datetime.time
    my_timedelta_property: datetime.timedelta


class MyRelatedModel(BaseModel, model_prefix="duality:related", model_version=1):
    relationship_to_child: MyChildModel = Relationship()  # type: ignore


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
                "name": "my_parent_property",
                "schema": "string",
            }
        ],
        displayName="MyModel",
    )


def test_child_model_to_dtdl() -> None:
    interface = Interface(
        id="dtmi:duality:child:my_child_model;1",
        contents=[
            {
                "@type": "Property",
                "name": "my_string_property",
                "schema": "string",
            },
            {
                "@type": "Property",
                "name": "my_int_property",
                "schema": "integer",
            },
            {
                "@type": "Property",
                "name": "my_float_property",
                "schema": "double",
            },
            {
                "@type": "Property",
                "name": "my_bool_property",
                "schema": "boolean",
            },
            {
                "@type": "Property",
                "name": "my_date_property",
                "schema": "date",
            },
            {
                "@type": "Property",
                "name": "my_datetime_property",
                "schema": "dateTime",
            },
            {
                "@type": "Property",
                "name": "my_time_property",
                "schema": "time",
            },
            {
                "@type": "Property",
                "name": "my_timedelta_property",
                "schema": "duration",
            },
        ],
        extends="dtmi:duality:my_model;2",
        displayName="MyChildModel",
    )
    assert MyChildModel.to_dict() == interface.dict()


def test_related_model_to_dtdl() -> None:
    """A model can contain a relationship to another one, which adds a relationship
    to the DTDL contents, whose target is the other model.
    """
    interface = Interface(
        id="dtmi:duality:related:my_related_model;1",
        contents=[
            {
                "@type": "Relationship",
                "name": "relationship_to_child",
                "target": str(MyChildModel.id),
            },
        ],
        displayName="MyRelatedModel",
    )
    assert MyRelatedModel.to_dict() == interface.dict()
