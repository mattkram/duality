import pytest

from duality.models import BaseModel


@pytest.fixture()
def model_class():
    """Create a new model class"""

    class MyModel(BaseModel):
        my_property: str

    yield MyModel


def test_get_adt_client(model_class):
    assert model_class.get_service_client() is not None
