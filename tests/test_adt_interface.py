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
