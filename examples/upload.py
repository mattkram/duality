from duality.adt import ADTClient
from examples.models import Dog
from examples.models import Person

adt_client = ADTClient()

adt_client.upload_model(Person)
adt_client.upload_model(Dog)


for i in range(1, 101):
    adt_client.upload_twin(
        Person(
            name=f"Person {i}",
            location=f"Location {i}",
            age=i,
        )
    )
    adt_client.upload_twin(
        Dog(
            name=f"Dog {i}",
            breed=f"Breed {i}",
            age=i,
        )
    )
