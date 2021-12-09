from duality.adt import ADTClient
from examples import models

adt_client = ADTClient()

adt_client.upload_model(models.Person)
adt_client.upload_model(models.Pet)
adt_client.upload_model(models.Dog)
adt_client.upload_model(models.Cat)
adt_client.upload_model(models.Terrier)


for i in range(1, 11):
    adt_client.upload_twin(
        models.Person(
            name=f"Person {i}",
            location=f"Location {i}",
            age=i,
        )
    )
    adt_client.upload_twin(
        models.Dog(
            name=f"Dog {i}",
            breed=f"Breed {i}",
            age=i,
        )
    )
    adt_client.upload_twin(
        models.Cat(
            name=f"Cat {i}",
            eye_color=f"Eye color {i}",
            age=i,
        )
    )

adt_client.upload_twin(
    models.Terrier(
        name="Bonnie",
        type="Westie",
        breed="Westie",
        age=13,
    )
)
