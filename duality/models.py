import os
from typing import Optional

from azure.digitaltwins.core import DigitalTwinsClient
from azure.identity import DefaultAzureCredential
from pydantic import BaseModel as _BaseModel


class BaseModel(_BaseModel):
    """Base model for all models within the duality framework.

    The metaclass of this base class is an "Interface" in the DTDL specification.

    """

    _service_client: Optional[DigitalTwinsClient] = None

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
