import time
from typing import Any
from typing import Generator
from typing import Type

import pydantic
import pytest
from azure.digitaltwins.core import DigitalTwinsModelData

from duality.adt import ADTClient
from duality.models import BaseModel


@pytest.fixture(scope="session")
def adt_client() -> ADTClient:
    return ADTClient()


class MyModel(BaseModel, model_prefix="duality"):
    my_property: str
    my_named_int_property: int = pydantic.Field(description="My Named Property")


ModelClass = Type[MyModel]


@pytest.fixture(scope="module")
def model_class() -> Generator[ModelClass, None, None]:
    """Create a new model class"""

    yield MyModel


def test_get_adt_client(adt_client: ADTClient) -> None:
    assert adt_client.service_client is not None


@pytest.fixture(scope="module")
def uploaded_model_class(
    adt_client: ADTClient, model_class: ModelClass
) -> Generator[DigitalTwinsModelData, None, None]:
    """Upload the class as an ADT model, and delete after using."""
    model = adt_client.upload_model(model_class)
    yield model
    adt_client.delete_model(model_class)


def test_upload_model(
    model_class: ModelClass, uploaded_model_class: DigitalTwinsModelData
) -> None:
    assert uploaded_model_class.id == uploaded_model_class.id


@pytest.fixture(scope="module")
def model_instance(model_class: ModelClass) -> BaseModel:
    return model_class(my_property="My Value", my_named_int_property=42)


@pytest.fixture(scope="module")
def uploaded_twin(
    adt_client: ADTClient,
    uploaded_model_class: DigitalTwinsModelData,
    model_instance: BaseModel,
) -> Generator[BaseModel, None, None]:
    twin = adt_client.upload_twin(model_instance)
    time.sleep(2)
    yield twin
    adt_client.delete_twin(model_instance)


def test_upload_twin(model_instance: MyModel, uploaded_twin: MyModel) -> None:
    assert model_instance is not uploaded_twin  # different instances
    assert model_instance.id == uploaded_twin.id
    assert model_instance.my_property == uploaded_twin.my_property
    assert model_instance.my_named_int_property == uploaded_twin.my_named_int_property


def delay_rerun(*_: Any) -> bool:
    time.sleep(2)
    return True


@pytest.mark.flaky(rerun_filter=delay_rerun)
def test_query_count(
    adt_client: ADTClient, model_class: ModelClass, uploaded_twin: MyModel
) -> None:
    assert adt_client.query.of_model(model_class, exact=False).count() == 1


@pytest.mark.flaky(rerun_filter=delay_rerun)
def test_query_all(
    adt_client: ADTClient, model_class: ModelClass, uploaded_twin: MyModel
) -> None:
    results = list(adt_client.query.of_model(model_class, exact=False).all())
    assert len(results) == 1
    model_instance = results[0]
    assert model_instance.id == uploaded_twin.id
    assert model_instance.my_property == uploaded_twin.my_property
    assert model_instance.my_named_int_property == uploaded_twin.my_named_int_property
