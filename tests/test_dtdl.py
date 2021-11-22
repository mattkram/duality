import json

import pydantic
import pytest

from duality.dtdl import DTMI
from duality.dtdl import Interface
from duality.dtdl import Property


@pytest.mark.parametrize(
    "kwargs",
    as_dict={
        "full": dict(scheme="dtmi", path="com:adt:dtsample:home", version=1),
        "partial_version_int": dict(path="com:adt:dtsample:home", version=1),
        "partial_version_float": dict(path="com:adt:dtsample:home", version=1.0),
        "partial_version_str": dict(path="com:adt:dtsample:home", version="1"),
        "partial_version_str_float": dict(path="com:adt:dtsample:home", version="1.0"),
    },
)
def test_dtmi_string_repr(kwargs):
    dtmi = DTMI(**kwargs)
    assert str(dtmi) == "dtmi:com:adt:dtsample:home;1"


def test_dtmi_from_string():
    dtmi = DTMI.from_string("dtmi:com:adt:dtsample:home;1")
    assert dtmi == DTMI(schema="dtmi", path="com:adt:dtsample:home", version=1)


@pytest.mark.parametrize(
    "version",
    as_dict={
        "too_low": 0,
        "too_high": 1_000_000_000,
        "decimal_float": 1.5,
        "decimal_string": "1.5",
        "zero-padded_string": "01",
    },
)
def test_dtmi_invalid_version_number(version):
    with pytest.raises(pydantic.ValidationError):
        DTMI(path="com:adt:dtsample:home", version=version)


def test_dtmi_comparison_case_sensitive():
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
)
def test_dtmi_path_validation(path):
    with pytest.raises(pydantic.ValidationError):
        DTMI(path=path, version=1)


def test_interface_from_dict():
    data = {
        "@id": {"scheme": "dtmi", "path": "com:adt:dtsample:home", "version": 1},
        "@type": "Interface",
        "@context": "dtmi:dtdl:context;2",
    }
    interface = Interface(**data)
    assert interface.id == "dtmi:com:adt:dtsample:home;1"
    assert interface.type == "Interface"
    assert interface.context == "dtmi:dtdl:context;2"
    assert interface.dict(exclude_unset=True) == data
    assert interface.json(exclude_unset=True) == json.dumps(data)


def test_property_from_dict():
    data = {
        "@type": "Property",
        "name": "my_property",
        "schema": "string",
        "displayName": "My Property",
    }
    property = Property(**data)
    assert property.type == "Property"
    assert property.dict() == data
