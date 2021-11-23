from duality.models import BaseModel


class Person(BaseModel, model_prefix="duality", model_version=2):
    name: str
    location: str
    age: int


class Dog(BaseModel, model_prefix="duality", model_version=2):
    name: str
    breed: str
    age: int
