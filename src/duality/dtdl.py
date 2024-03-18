"""Base pydantic models (schemas) to handle serialization/deserialization of ADT."""

from string import digits
from typing import Any
from typing import Callable
from typing import Generator
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union

import pydantic


class _BaseModel(pydantic.BaseModel):
    class Config:
        allow_population_by_field_name = True

    def dict(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        """Override to always use field alias."""
        kwargs.setdefault("by_alias", True)
        kwargs.setdefault("exclude_none", True)
        return super().dict(*args, **kwargs)

    def json(self, *args: Any, **kwargs: Any) -> str:
        """Override to always use field alias."""
        kwargs.setdefault("by_alias", True)
        kwargs.setdefault("exclude_none", True)
        return super().json(*args, **kwargs)


class DTMI(str):
    """https://github.com/Azure/opendigitaltwins-dtdl/blob/master/DTDL/v2/dtdlv2.md#digital-twin-model-identifier"""

    def __new__(
        cls,
        /,
        string: str = None,
        *,
        scheme: str = "dtmi",
        path: str = "",
        version: int = 1,
    ) -> "DTMI":
        """Allow construction via keywords, or just as a string.
        e.g. DTMI("dtmi:path;1") == DTMI(scheme="dtmi", path="path", version=1)
        """
        if string is not None:
            return str(string)  # type: ignore
        version = int(float(version))
        return f"{scheme}:{path};{version}"  # type: ignore

    @classmethod
    def parts_from_string(cls, string: str) -> Tuple[str, str, str]:
        scheme, _, rest = string.partition(":")
        path, _, version = rest.rpartition(";")
        return scheme, path, version

    @classmethod
    def from_string(cls, string: str) -> "DTMI":
        """Construct a DTMI from a string representation."""
        return cls(string)

    @classmethod
    def __get_validators__(cls) -> Generator[Callable[[Any], "DTMI"], None, None]:
        yield cls.validate_dict
        yield cls.validate_path
        yield cls.validate_version

    @classmethod
    def validate_dict(cls, v: Any) -> "DTMI":
        """Convert a dictionary to a DTMI object"""
        if isinstance(v, dict):
            return DTMI(**v)
        return v

    @classmethod
    def validate_path(cls, v: "DTMI") -> "DTMI":
        """Validate the path segments."""
        _, path, _ = cls.parts_from_string(v)
        if not path:
            raise ValueError("Path must have at least one ':'")
        segments = path.split(":")
        for segment in segments:
            if segment[0] in digits:
                raise ValueError("Segment cannot start with number")
            if segment[-1] == "_":
                raise ValueError("Segment cannot end with underscore")
        return v

    @classmethod
    def validate_version(cls, v: Any) -> "DTMI":
        """Version must be an integer between [1, 999,999,999], inclusive."""
        scheme, path, version = cls.parts_from_string(v)
        if isinstance(version, str):
            if version[0] == "0":
                raise ValueError("Zero-padded version strings are not allowed.")
            version = float(version)  # type: ignore
        float_val = float(version)
        int_val = int(version)
        if int_val != float_val:
            raise ValueError("Version cannot be a decimal float.")
        if not (1 <= int_val <= 999_999_999):
            raise ValueError("Version must be in range [1, 999_999_999], inclusive.")
        return DTMI(scheme=scheme, path=path, version=int_val)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, (DTMI, str)):
            return False
        return str(self) == str(other)


class IRI(str):
    pass


class Telemetry(_BaseModel): ...


class Property(_BaseModel):
    type: str = pydantic.Field("Property", alias="@type")
    name: str
    schema_: str = pydantic.Field(alias="schema")
    displayName: Optional[str]


class Relationship(_BaseModel):
    type: str = pydantic.Field("Relationship", alias="@type")
    name: str
    id: Optional[DTMI]
    comment: Optional[str]
    description: Optional[str]
    displayName: Optional[str]
    maxMultiplicity: Optional[int] = pydantic.Field(gt=1)
    minMultiplicity: Optional[int]
    properties: Optional[List[Property]]
    target: Optional[DTMI]
    writable: Optional[bool]


class Schema(str): ...


class Command(_BaseModel): ...


class Component(_BaseModel):
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


ContentsItem = Union[
    # "Telemetry",
    "Property",
    # "Command",
    "Relationship",
    # "Component",
]


class Interface(_BaseModel):
    id: DTMI = pydantic.Field(..., alias="@id")
    type: str = pydantic.Field("Interface", alias="@type")
    context: str = pydantic.Field("dtmi:dtdl:context;2", alias="@context")
    comment: str = ""
    contents: Optional[List[ContentsItem]] = pydantic.Field(default_factory=list)
    description: str = ""
    displayName: str = ""
    extends: Optional[DTMI] = None
    schemas: List["Schema"] = pydantic.Field(default_factory=list)
