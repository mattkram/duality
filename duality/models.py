from string import digits

import pydantic

from .base import BaseModel


class DTMI(BaseModel):
    """https://github.com/Azure/opendigitaltwins-dtdl/blob/master/DTDL/v2/dtdlv2.md#digital-twin-model-identifier"""

    scheme: str = "dtmi"
    path: str
    version: str

    def __str__(self) -> str:
        """Construct the Digital Twin Model Identifier."""
        return f"{self.scheme}:{self.path};{self.version}"

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
                raise pydantic.ValidationError("Segment cannot start with number")
            if segment[-1] == "_":
                raise pydantic.ValidationError("Segment cannot end with underscore")
        return v
