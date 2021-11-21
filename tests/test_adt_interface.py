import pytest

from duality.models import BaseModel


@pytest.fixture()
def model_class():
    """Create a new model class"""

    class MyModel(BaseModel, model_prefix="duality"):
        my_property: str

    yield MyModel


def test_get_adt_client(model_class):
    assert model_class.get_service_client() is not None


@pytest.fixture()
def uploaded_model_class(model_class):
    model = model_class.upload_to_adt()
    yield model
    model_class.delete_from_adt()


def test_upload_model(uploaded_model_class):
    assert uploaded_model_class is not None
