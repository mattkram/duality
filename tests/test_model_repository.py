from pathlib import Path

from duality.models import BaseModel
from duality.models import Relationship
from duality.repository import ModelRepository


class MyBaseModel(BaseModel, root=True, ignore=True):
    """A new base model, with a clean inheritance hierarchy, which won't get exported."""


class MyModel(MyBaseModel, model_prefix="duality", model_version=2):
    my_parent_property: str


class MyChildModel(MyModel, model_prefix="duality:child", model_version=1):
    my_string_property: str
    my_int_property: int


class MyRelatedModel(MyBaseModel, model_prefix="duality:related", model_version=1):
    relationship_to_child: MyChildModel = Relationship()  # type: ignore


def test_export_model_tree_to_repository(tmp_path: Path) -> None:
    repo = ModelRepository(base_dir=tmp_path)
    repo.export_model_tree(MyBaseModel)

    exported_files = {p.name for p in tmp_path.glob("*")}
    assert exported_files == {
        "dtmi:duality:my_model;2.json",
        "dtmi:duality:child:my_child_model;1.json",
        "dtmi:duality:related:my_related_model;1.json",
    }
