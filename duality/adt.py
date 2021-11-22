import os
from typing import Type

from azure.core.exceptions import ResourceExistsError
from azure.digitaltwins.core import DigitalTwinsClient
from azure.identity import DefaultAzureCredential

from duality.models import BaseModel


class ADTClient:
    """An Azure Digital Twins client wrapper to interface between duality models and ADT."""

    _service_client: DigitalTwinsClient

    @property
    def service_client(self) -> DigitalTwinsClient:
        """Construct an Azure Digital Twins client.

        Reads credentials from the following environment variables, which can be placed in a `.env` file:

            * `AZURE_URL`
            * `AZURE_TENANT_ID`
            * `AZURE_CLIENT_ID`
            * `AZURE_CLIENT_SECRET`

        """
        if getattr(self, "_service_client", None) is None:
            url = os.getenv("AZURE_URL", "")
            credential = DefaultAzureCredential()
            self._service_client = DigitalTwinsClient(url, credential)

        return self._service_client

    def upload_model(self, model: Type[BaseModel], exist_ok=True):
        sc = self.service_client
        try:
            adt_model = sc.create_models([model.to_dtdl()])
        except ResourceExistsError:
            if not exist_ok:
                raise
            return sc.get_model(model.id)
        else:
            return adt_model[0]

    def delete_model(self, model: Type[BaseModel]) -> None:
        self.service_client.delete_model(model.id)
