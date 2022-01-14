"""The duality model repository.

Allows export and management of models exported from duality classes to DTDL schemas.

"""
import json
from pathlib import Path
from typing import Type
from typing import Union

from duality.models import BaseModel


class ModelRepository:
    """The ModelRepository allows export and management of a duality class hierarchy to DTDL files.

    Attributes:
        base_dir: The base directory in which to store the DTDL files.

    """

    def __init__(self, base_dir: Union[Path, str]):
        self.base_dir = Path(base_dir)

    def export_model_tree(self, root_model: Type[BaseModel]) -> None:
        """Export a model inheritance tree to a directory.

        Args:
            root_model: The duality model root to export.

        """
        self.base_dir.mkdir(parents=True, exist_ok=True)
        for model_id, model_class in root_model.class_registry.items():
            dtdl_dict = model_class.to_dict()

            with (self.base_dir / f"{model_id}.json").open("w") as fp:
                json.dump(dtdl_dict, fp, indent=2)
