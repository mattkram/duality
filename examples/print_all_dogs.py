from rich import print

from duality.adt import ADTClient
from examples.models import Dog

adt_client = ADTClient()
print(list(adt_client.query.of_model(Dog).all()))
