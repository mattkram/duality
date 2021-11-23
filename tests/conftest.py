import pytest


def _monkey_patch_parametrize() -> None:
    """Monkeypatch parametrize to add `as_dict` argument.

    Not a fixture since needs to occur during import.

    """
    _orig_parametrize = pytest.mark.parametrize

    def _new_parametrize(*args, as_dict=None, **kwargs):  # type: ignore
        def wrapped(f):  # type: ignore
            if as_dict is not None:
                kwargs["ids"] = as_dict.keys()
                kwargs["argvalues"] = as_dict.values()
            return _orig_parametrize(*args, **kwargs)(f)

        return wrapped

    setattr(pytest.mark, "parametrize", _new_parametrize)


_monkey_patch_parametrize()
