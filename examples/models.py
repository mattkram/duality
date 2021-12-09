from duality.models import BaseModel


class Person(BaseModel, model_prefix="duality", model_version=1):
    name: str
    location: str
    age: int


class Pet(BaseModel, model_prefix="duality:pets", model_version=1):
    name: str
    age: int


class Dog(Pet, model_prefix="duality", model_version=1):
    breed: str


class Cat(Pet, model_prefix="duality:pets", model_version=1):
    eye_color: str


class Terrier(Dog, model_prefix="duality:pets:dog:terrier", model_version=1):
    type: str
