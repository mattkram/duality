import os
from typing import Any
from typing import Optional

from azure.digitaltwins.core import DigitalTwinsClient
from azure.identity import DefaultAzureCredential
from pydantic import BaseModel as _BaseModel


class BaseModel(_BaseModel):
    """Base model for all models within the duality framework.

    The metaclass of this base class is an "Interface" in the DTDL specification.

    """

    _special_fields: dict[str, str] = {}  # mapping of name to alias
    _service_client: Optional[DigitalTwinsClient] = None

    def __init_subclass__(cls, **kwargs: Any) -> None:
        """Capture any field with an alias starting with @, so we can use those aliases in dict()."""
        cls._special_fields = {}
        for name, field in cls.__fields__.items():
            if field.alias.startswith("@"):
                cls._special_fields[name] = field.alias

    @classmethod
    def get_service_client(cls):
        """Construct an Azure Digital Twins client.

        Reads credentials from the following environment variables, which can be placed in a `.env` file:

            * `AZURE_URL`
            * `AZURE_TENANT_ID`
            * `AZURE_CLIENT_ID`
            * `AZURE_CLIENT_SECRET`

        """
        if cls._service_client is None:
            url = os.getenv("AZURE_URL", "")
            credential = DefaultAzureCredential()
            cls._service_client = DigitalTwinsClient(url, credential)

        return cls._service_client

    def dict(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        """Generate the dictionary representation, with handling of special fields."""
        result = {}
        for key, value in super().dict(*args, **kwargs).items():
            if key in self._special_fields:
                key = self._special_fields[key]
            result[key] = value

        return result
