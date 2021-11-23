import os
from typing import Generator
from typing import Type

from azure.core.exceptions import ResourceExistsError
from azure.digitaltwins.core import DigitalTwinsClient
from azure.identity import DefaultAzureCredential

from duality.models import BaseModel


class ADTQuery:
    def __init__(self, client: DigitalTwinsClient):
        self._client = client
        self._selector = "*"
        self._wheres: list[str] = []

    def _execute(self):
        clauses = [
            f"SELECT {self._selector}",
            "FROM digitaltwins",
        ]
        if self._wheres:
            clauses.append("WHERE")
            for where in self._wheres:
                clauses.append(where)
                clauses.append("AND")
            clauses.pop(-1)

        query_string = " ".join(clauses)
        return self._client.query_twins(query_string)

    def of_model(self, model_class: Type[BaseModel], exact: bool = False):
        """Filter results to return instances of a single model type."""
        if exact:
            clause = f"IS_OF_MODEL('{model_class.id}', exact)"
        else:
            clause = f"IS_OF_MODEL('{model_class.id}')"
        self._wheres.append(clause)
        return self

    def count(self) -> int:
        """Return the number of objects returned by the query."""
        self._selector = "COUNT()"
        result = next(self._execute())
        return result["COUNT"]

    def all(self) -> Generator[BaseModel, None, None]:
        """Return a generator of all objects returned by the query."""
        for data in self._execute():
            yield BaseModel.from_twin_dtdl(**data)


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

    @property
    def query(self) -> ADTQuery:
        return ADTQuery(self.service_client)

    def upload_model(self, model: Type[BaseModel], exist_ok=True):
        sc = self.service_client
        try:
            adt_model = sc.create_models([model.to_interface().dict()])
        except ResourceExistsError:
            if not exist_ok:
                raise
            return sc.get_model(model.id)
        else:
            return adt_model[0]

    def delete_model(self, model: Type[BaseModel]) -> None:
        self.service_client.delete_model(model.id)

    def upload_twin(self, instance: BaseModel) -> BaseModel:
        def create_instance(_, data, __):
            return instance.__class__(**data)

        return self.service_client.upsert_digital_twin(
            instance.id, instance.to_twin_dtdl(), cls=create_instance
        )

    def delete_twin(self, instance: BaseModel):
        self.service_client.delete_digital_twin(instance.id)
