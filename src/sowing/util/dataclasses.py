from dataclasses import fields


def repr_default(cls):
    """Replace a dataclass __repr__ to omit fields with default values."""

    def cls_repr(self):
        args = ", ".join(
            f"{field.name}={getattr(self, field.name)!r}"
            for field in fields(cls)
            if getattr(self, field.name) != field.default and field.repr
        )
        return f"{cls.__qualname__}({args})"

    cls.__repr__ = cls_repr
    return cls
