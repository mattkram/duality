from typing import Any

from pydantic import BaseModel as _BaseModel


class BaseModel(_BaseModel):
    """Base model for all models within the duality framework."""

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
