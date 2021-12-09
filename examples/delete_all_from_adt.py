from duality.adt import ADTClient
from examples import models  # noqa: F401, required to fill class registry


adt_client = ADTClient()
for twin in adt_client.query.all():
    try:
        adt_client.delete_twin(twin)
    except Exception:
        pass

for model in [models.Terrier, models.Dog, models.Cat, models.Pet, models.Person]:
    adt_client.delete_model(model)
