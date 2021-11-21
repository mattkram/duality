"""Base pydantic models (schemas) to handle serialization/deserialization of ADT."""
from string import digits
from typing import Any
from typing import Optional
from typing import Set
from typing import Union

import pydantic

ContentsItem = Union["Telemetry", "Property", "Command", "Relationship", "Component"]


class BaseModel(pydantic.BaseModel):

    _special_fields: dict[str, str] = {}  # mapping of name to alias

    def __init_subclass__(cls, **kwargs: Any) -> None:
        """Capture any field with an alias starting with @, so we can use those aliases in dict()."""
        cls._special_fields = {}
        for name, field in cls.__fields__.items():
            if field.alias.startswith("@"):
                cls._special_fields[name] = field.alias

    def dict(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        """Generate the dictionary representation, with handling of special fields."""
        result = {}
        for key, value in super().dict(*args, **kwargs).items():
            if key in self._special_fields:
                key = self._special_fields[key]
            result[key] = value

        return result


class DTMI(BaseModel):
    """https://github.com/Azure/opendigitaltwins-dtdl/blob/master/DTDL/v2/dtdlv2.md#digital-twin-model-identifier"""

    scheme: str = "dtmi"
    path: str
    version: int

    def __str__(self) -> str:
        """Construct the Digital Twin Model Identifier."""
        return f"{self.scheme}:{self.path};{self.version}"

    @classmethod
    def from_string(cls, string: str) -> "DTMI":
        """Construct a DTMI from a string representation."""
        scheme, _, rest = string.partition(":")
        path, _, version = rest.rpartition(";")
        return DTMI(scheme=scheme, path=path, version=version)

    @property
    def segments(self) -> list[str]:
        """Split the path into segments."""
        return self.path.split(":")

    @pydantic.validator("path")
    def validate_path(cls, v: str) -> str:
        """Validate the path segments."""
        segments = v.split(":")
        for segment in segments:
            if segment[0] in digits:
                raise ValueError("Segment cannot start with number")
            if segment[-1] == "_":
                raise ValueError("Segment cannot end with underscore")
        return v

    @pydantic.validator("version", pre=True)
    def validate_version(cls, v: Any) -> int:
        """Version must be an integer between [1, 999,999,999], inclusive."""
        if isinstance(v, str):
            if v[0] == "0":
                raise ValueError("Zero-padded version strings are not allowed.")
            v = float(v)
        float_val = float(v)
        int_val = int(v)
        if int_val != float_val:
            raise ValueError("Version cannot be a decimal float.")
        if not (1 <= int_val <= 999_999_999):
            raise ValueError("Version must be in range [1, 999_999_999], inclusive.")
        return int_val


class Interface(BaseModel):
    id: DTMI = pydantic.Field(..., alias="@id")
    type: str = pydantic.Field("interface", alias="@type")
    context: str = pydantic.Field("dtmi:dtdl:context;2", alias="@context")
    comment: str = ""
    contents: Optional[Set["ContentsItem"]] = pydantic.Field(default_factory=set)
    description: str = ""
    displayName: str = ""
    extends: Set["Interface"] = pydantic.Field(default_factory=set)
    schemas: Set["Schema"] = pydantic.Field(default_factory=set)


class IRI(str):
    pass


class Telemetry(BaseModel):
    ...


class Property(BaseModel):
    ...


class Relationship(BaseModel):
    ...


class Schema(str):
    ...


class Command(BaseModel):
    ...


class Component(BaseModel):
    type: IRI = pydantic.Field(..., alias="@type")
    name: str = pydantic.Field(
        ...,
        min_length=1,
        max_length=64,
        regex="^[a-zA-Z](?:[a-zA-Z0-9_]*[a-zA-Z0-9])?$",
    )
    schema_: "Interface" = pydantic.Field(..., alias="schema")
    id: DTMI = pydantic.Field(alias="@id")
    comment: Optional[str] = pydantic.Field(min_length=1, max_length=512)
    description: Optional[str] = pydantic.Field(min_length=1, max_length=512)
    displayName: Optional[str] = pydantic.Field(min_length=1, max_length=512)
    # id: Optional[UUID] = pydantic.Field(alias="@dtId")
