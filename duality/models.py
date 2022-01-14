import datetime
import re
import uuid
from typing import Any
from typing import Dict
from typing import Optional
from typing import Type

import pydantic

from duality.dtdl import DTMI
from duality.dtdl import Interface
from duality.dtdl import Property

# A mapping of Python types to DTDL primitive schemas
PRIMITIVE_SCHEMA_MAP: Dict[Type, str] = {
    str: "string",
    int: "integer",
    float: "double",
    bool: "boolean",
    datetime.date: "date",
    datetime.datetime: "dateTime",
    datetime.time: "time",
    datetime.timedelta: "duration",
}


def _camel_to_snake(name: str) -> str:
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
        return _camel_to_snake(cls.__name__)

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


def _get_schema(field_type: Type) -> str:
    """Generate a schema string for a python field type."""
    try:
        return PRIMITIVE_SCHEMA_MAP[field_type]
    except KeyError:
        raise ValueError(f"Cannot handle field of type {field_type} yet")


class BaseModel(pydantic.BaseModel, metaclass=ModelMetaclass):
    """Base model for all models within the duality framework.

    The metaclass of this base class is an "Interface" in the DTDL specification.

    """

    id: str = pydantic.Field(alias="$dtId", default_factory=lambda: str(uuid.uuid4()))

    _class_registry: dict[str, Type["BaseModel"]] = {}

    def __init_subclass__(
        cls, model_prefix: str = "", model_name: str = "", model_version: int = 1
    ):
        """Handle ability of subclasses to override."""
        cls.model_prefix = model_prefix
        cls.model_name = model_name
        cls.model_version = model_version
        cls._class_registry[cls.id] = cls

    @property
    def model_id(self) -> DTMI:
        """The DTMI of the model (class-itself)."""
        return self.__class__.id  # type: ignore

    @classmethod
    def to_interface(cls) -> Interface:
        contents = []
        ignored = {"id"}

        base_fields = cls.__base__.__fields__  # type: ignore
        for name, field in cls.__fields__.items():
            if name not in ignored and name not in base_fields:
                prop = Property(
                    name=name,
                    schema=_get_schema(field.type_),
                    displayName=field.field_info.description,
                )
                contents.append(prop)

        base = cls.__base__
        extends: Optional[str] = None
        if issubclass(base, BaseModel) and base != BaseModel:
            extends = base.id

        return Interface(
            id=cls.id, displayName=cls.__name__, contents=contents, extends=extends
        )

    @classmethod
    def to_dict(cls) -> Dict[str, Any]:
        """Return the class interface as a DTDL schema dictionary."""
        return cls.to_interface().dict()

    @classmethod
    def from_twin_dtdl(cls, **data: Any) -> "BaseModel":
        """Construct an object based on ADT response data, using the class registry."""
        model_id = data["$metadata"]["$model"]
        class_ = cls._class_registry[model_id]
        return class_(**data)

    def to_twin_dtdl(self) -> dict[str, Any]:
        """Return a dtdl representation of the instance."""
        data = {"$metadata": {"$model": self.model_id}}
        ignored = {"id"}
        for key in self.__fields__:
            if key not in ignored:
                data[key] = getattr(self, key)
        return data
