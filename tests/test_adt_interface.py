import pytest

from duality.adt import ADTClient
from duality.models import BaseModel


@pytest.fixture(scope="session")
def adt_client():
    return ADTClient()


@pytest.fixture()
def model_class():
    """Create a new model class"""

    class MyModel(BaseModel, model_prefix="duality"):
        my_property: str

    yield MyModel


def test_get_adt_client(adt_client):
    assert adt_client.service_client is not None


@pytest.fixture()
def uploaded_model_class(adt_client, model_class):
    """Upload the class as an ADT model, and delete after using."""
    model = adt_client.upload_model(model_class)
    yield model
    adt_client.delete_model(model_class)


def test_upload_model(model_class, uploaded_model_class):
    assert uploaded_model_class.id == uploaded_model_class.id


@pytest.fixture()
def model_instance(model_class):
    return model_class(my_property="My Value")


@pytest.fixture()
def uploaded_twin(adt_client, uploaded_model_class, model_instance):
    twin = adt_client.upload_twin(model_instance)
    yield twin
    adt_client.delete_twin(model_instance)


def test_upload_twin(model_instance, uploaded_twin):
    assert model_instance is not uploaded_twin  # different instances
    assert model_instance.id == uploaded_twin.id
    assert model_instance.my_property == uploaded_twin.my_property
