import datetime
import re
import uuid
from typing import Any
from typing import ClassVar
from typing import Optional
from typing import Type
from typing import Union

import pydantic

from duality import dtdl

# A mapping of Python types to DTDL primitive schemas
PRIMITIVE_SCHEMA_MAP: dict[Type, str] = {
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
    def id(cls) -> dtdl.DTMI:
        return dtdl.DTMI(
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

    class_registry: ClassVar[dict[str, Type["BaseModel"]]] = {}

    __ignore_during_export__: ClassVar[bool] = False

    def __init_subclass__(
        cls,
        model_prefix: str = "",
        model_name: str = "",
        model_version: int = 1,
        root: bool = False,
        ignore: bool = False,
    ):
        """Handle ability of subclasses to override."""
        cls.model_prefix = model_prefix
        cls.model_name = model_name
        cls.model_version = model_version
        cls.__ignore_during_export__ = ignore

        if root:
            # Define a new model root by giving it its own empty registry
            cls.class_registry = {}

        if not ignore:
            cls.class_registry[cls.id] = cls

    @property
    def model_id(self) -> dtdl.DTMI:
        """The DTMI of the model (class-itself)."""
        return self.__class__.id  # type: ignore

    @classmethod
    def to_interface(cls) -> dtdl.Interface:
        contents: list[Union[dtdl.Property, dtdl.Relationship]] = []
        ignored = {"id"}

        base_fields = cls.__base__.__fields__  # type: ignore
        for name, field in cls.__fields__.items():
            if name not in ignored and name not in base_fields:
                if isinstance(field.default, Relationship):
                    relationship = dtdl.Relationship(
                        name=name,
                        target=field.type_.id,
                    )
                    contents.append(relationship)
                else:
                    prop = dtdl.Property(
                        name=name,
                        schema=_get_schema(field.type_),
                        displayName=field.field_info.description,
                    )
                    contents.append(prop)

        base = cls.__base__
        extends: Optional[str] = None
        if (
            issubclass(base, BaseModel)
            and base != BaseModel
            and not base.__ignore_during_export__
        ):
            extends = base.id

        return dtdl.Interface(
            id=cls.id, displayName=cls.__name__, contents=contents, extends=extends
        )

    @classmethod
    def to_dict(cls) -> dict[str, Any]:
        """Return the class interface as a DTDL schema dictionary."""
        return cls.to_interface().dict()

    @classmethod
    def from_twin_dtdl(cls, **data: Any) -> "BaseModel":
        """Construct an object based on ADT response data, using the class registry."""
        model_id = data["$metadata"]["$model"]
        class_ = cls.class_registry[model_id]
        return class_(**data)

    def to_twin_dtdl(self) -> dict[str, Any]:
        """Return a dtdl representation of the instance."""
        data = {"$metadata": {"$model": self.model_id}}
        ignored = {"id"}
        for key in self.__fields__:
            if key not in ignored:
                data[key] = getattr(self, key)
        return data


class Relationship:
    """A relationship from one Model to another."""

    # TODO: Relationship should be able to be inherited from, such that sub-types can
    #  define attributes that can be stored on the relationships (i.e. edges) themselves.
