import json
from typing import Any
from typing import Union

import pydantic
import pytest

from duality.dtdl import DTMI
from duality.dtdl import Interface
from duality.dtdl import Property
from duality.dtdl import Relationship


@pytest.mark.parametrize(
    "kwargs",
    as_dict={
        "full": dict(scheme="dtmi", path="com:adt:dtsample:home", version=1),
        "partial_version_int": dict(path="com:adt:dtsample:home", version=1),
        "partial_version_float": dict(path="com:adt:dtsample:home", version=1.0),
        "partial_version_str": dict(path="com:adt:dtsample:home", version="1"),
        "partial_version_str_float": dict(path="com:adt:dtsample:home", version="1.0"),
    },
)  # type: ignore
def test_dtmi_string_repr(kwargs: dict[str, Any]) -> None:
    dtmi = DTMI(**kwargs)
    assert str(dtmi) == "dtmi:com:adt:dtsample:home;1"


def test_dtmi_from_string() -> None:
    dtmi = DTMI.from_string("dtmi:com:adt:dtsample:home;1")
    assert dtmi == DTMI(scheme="dtmi", path="com:adt:dtsample:home", version=1)


@pytest.mark.parametrize(
    "version",
    as_dict={
        "too_low": 0,
        "too_high": 1_000_000_000,
        "decimal_float": 1.5,
        "decimal_string": "1.5",
        "zero-padded_string": "01",
    },
)  # type: ignore
def test_dtmi_invalid_version_number(version: Union[int, float, str]) -> None:
    with pytest.raises(pydantic.ValidationError):
        Interface(id="dtmi:com:adt:dtsample:home;{version}")


def test_dtmi_comparison_case_sensitive() -> None:
    string = "dtmi:com:adt:dtsample:home;1"
    lower = DTMI.from_string(string)
    upper = DTMI.from_string(string.upper())
    assert lower != upper


@pytest.mark.parametrize(
    "path",
    as_dict={
        "leading_number": "com:1something:dtsample:home",
        "trailing_underscore": "com:something_:dtsample:home",
    },
)  # type: ignore
def test_dtmi_path_validation(path: str) -> None:
    with pytest.raises(pydantic.ValidationError):
        Interface(id=DTMI(path=path, version=1))


def test_interface_from_dict() -> None:
    data = {
        "@id": {"scheme": "dtmi", "path": "com:adt:dtsample:home", "version": 1},
        "@type": "Interface",
        "@context": "dtmi:dtdl:context;2",
    }
    expected = {
        "@id": "dtmi:com:adt:dtsample:home;1",
        "@type": "Interface",
        "@context": "dtmi:dtdl:context;2",
    }
    interface = Interface(**data)
    assert interface.id == "dtmi:com:adt:dtsample:home;1"
    assert interface.type == "Interface"
    assert interface.context == "dtmi:dtdl:context;2"
    assert interface.dict(exclude_unset=True) == expected
    assert interface.json(exclude_unset=True) == json.dumps(expected)


def test_property_from_dict() -> None:
    data = {
        "@type": "Property",
        "name": "my_property",
        "schema": "string",
        "displayName": "My Property",
    }
    property = Property(**data)
    assert property.type == "Property"
    assert property.dict() == data


def test_relationship_from_dict() -> None:
    relationship = Relationship(
        name="my_relationship",
        target="dtmi:com:adt:dtsample:home;1",
        id="dtmi:com:adt:dtsample:relationship;1",
    )
    assert relationship.id == "dtmi:com:adt:dtsample:relationship;1"
    assert relationship.type == "Relationship"
    assert relationship.name == "my_relationship"
    assert relationship.target == "dtmi:com:adt:dtsample:home;1"
