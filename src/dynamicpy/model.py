import sys
import typing
from abc import ABCMeta
from typing import Any, Callable, Dict, Iterator, List, Mapping, Optional, Type, Union

from typeguard import TypeCheckError, check_type
from typing_extensions import Self


def field(
    *,
    default: Any = None,
    strict: bool = True,
    cast: Optional[Callable] = None,
) -> Any:
    opts = FieldOptions()
    opts.default = default
    opts.strict = strict
    opts.cast = cast

    return opts


class FieldOptions:
    def __init__(self) -> None:
        self.cast: Union[Callable, None]
        self.default: Any
        self.strict: bool


class FieldMetadata:
    def __init__(self, name: str, annotation: Type, opts: FieldOptions) -> None:
        self.name: str = name
        self.annotation = annotation
        self.options: FieldOptions = opts

    def process(self, values: Dict[str, Any]) -> Any:
        value = values.get(self.name, self.options.default)

        if not self.options.strict:
            return value

        try:
            return check_type(value, self.annotation)
        except TypeCheckError as e:
            if isinstance(value, dict):
                factory = self.get_factory()
                if factory is not None:
                    return factory(value)
            if self.options.cast is not None:
                return self.options.cast(value)

            raise TypeError(
                f"Value of type {type(value)} is not assignable to field '{self.name}'"
            ) from e

    def get_factory(self) -> Optional[Callable]:
        if typing.get_origin(self.annotation) is Union:
            types = typing.get_args(self.annotation)
        else:
            types = (self.annotation,)

        factories = [getattr(t, "from_dict") for t in types if hasattr(t, "from_dict")]
        if len(factories) > 1:
            raise TypeError(f"Multiple options for loading '{self.name}'")
        return next(iter(factories), None)

    def __get__(self, *_):
        raise AttributeError("Cannot access attributes of non-instance models")


class ModelMeta(ABCMeta):
    def __init__(self, *args) -> None:
        super().__init__(*args)
        self._fields: List[FieldMetadata] = []
        self._process_fields()

    def _process_fields(self) -> None:
        try:
            annotaions: Dict[str, Union[Type, str]] = self.__dict__["__annotations__"]
            globals = sys.modules[self.__module__].__dict__
            locals = dict(vars(self))
        except (AttributeError, KeyError):
            return
        for name, ann in annotaions.items():
            if name.startswith("_"):
                continue

            opts = getattr(self, name, None)
            if not isinstance(opts, FieldOptions):
                opts = field(default=opts)

            resolved = ann if not isinstance(ann, str) else eval(ann, globals, locals)
            metadata = FieldMetadata(name, resolved, opts)
            self._fields.append(metadata)
            setattr(self, name, metadata)


class Model(Mapping[str, Any], metaclass=ModelMeta):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        values: Dict[str, Any] = kwargs

        nargs = len(args)
        nfields = len(self._fields)
        if nargs > nfields:
            raise TypeError(
                f"'{type(self).__name__}' has {nfields} field{'s' if nfields > 0 else ''} but {nargs} were given"
            )

        for i, arg in enumerate(args):
            values[self._fields[i].name] = arg

        for field in self._fields:
            setattr(self, field.name, field.process(values))

    @classmethod
    def from_dict(cls, values: Dict[str, Any]) -> Self:
        return cls(**values)

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}({', '.join(f'{k}={repr(v)}' for k, v in self.items())})"
        )

    def __iter__(self) -> Iterator:
        return (f.name for f in self._fields)

    def __len__(self) -> int:
        return len(self._fields)

    def __contains__(self, key: str) -> bool:
        return key in iter(self)

    def __getitem__(self, key: str) -> Any:
        if key not in self:
            raise KeyError(f"Unknown field name '{key}'")
        return getattr(self, key)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, type(self)) and all(self[k] == other[k] for k in self)
