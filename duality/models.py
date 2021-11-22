import re

import pydantic

from duality.dtdl import DTMI


def camel_to_snake(name):
    name = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", name).lower()


class ModelMetaclass(pydantic.main.ModelMetaclass):
    """The model metaclass supplements the normal class behavior.

    It is used within duality to more directly represent attributes of the class itself,
    which generally map to the ADT Model associated with the class.

    """

    __model_prefix__: str
    __model_name__: str
    __model_version__: int

    @property
    def model_prefix(cls) -> str:
        """The model prefix represents all of the components of the id between the "dtmi:" literal
        and the class name (last part).

        """
        # TODO: When not specified, this should be derived from the MRO
        return cls.__model_prefix__

    @model_prefix.setter
    def model_prefix(cls, value: str) -> None:
        cls.__model_prefix__ = value

    @property
    def model_name(cls) -> str:
        """The model name is either specified on the class, or is the snake-case version of the class name."""
        if cls.__model_name__:
            return cls.__model_name__
        return camel_to_snake(cls.__name__)

    @model_name.setter
    def model_name(cls, value: str) -> None:
        cls.__model_name__ = value

    @property
    def model_version(cls) -> int:
        return cls.__model_version__

    @model_version.setter
    def model_version(cls, value: int) -> None:
        cls.__model_version__ = int(value)

    @property
    def id(cls) -> "DTMI":
        return DTMI(
            path=f"{cls.model_prefix}:{cls.model_name}",
            version=cls.model_version,
        )


class BaseModel(pydantic.BaseModel, metaclass=ModelMetaclass):
    """Base model for all models within the duality framework.

    The metaclass of this base class is an "Interface" in the DTDL specification.

    """

    def __init_subclass__(
        cls, model_prefix: str = "", model_name: str = "", model_version: int = 1
    ):
        """Handle ability of subclasses to override."""
        cls.model_prefix = model_prefix
        cls.model_name = model_name
        cls.model_version = model_version

    @classmethod
    def to_dtdl(cls):
        return {
            "@id": cls.id,
            "@type": "Interface",
            "@context": "dtmi:dtdl:context;2",
            "displayName": cls.__name__,
            "contents": [
                {"@type": "Property", "name": "my_property", "schema": "string"},
                # {
                #     "@type": "Telemetry",
                #     "name": "ComponentTelemetry1",
                #     "schema": "integer",
                # },
            ],
        }
