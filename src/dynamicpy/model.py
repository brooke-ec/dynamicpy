import sys
import typing
from abc import ABCMeta
from typing import Any, Callable, Dict, Iterator, List, Mapping, Optional, Type, Union

from typeguard import TypeCheckError, check_type
from typing_extensions import Self

__all__ = ("Model", "field")


def field(
    *,
    default: Any = None,
    strict: bool = True,
    cast: Optional[Callable] = None,
) -> Any:
    """Configure a `Model`'s field with advanced options.

    Parameters
    ----------
    default : Any, optional
        The default value if this field is not specified.
    strict : bool, optional
        Wether this field should be type-checked, by default True
    cast : Optional[Callable], optional
        A function to cast incorrectly typed values, by default None
    """
    opts = FieldOptions()
    opts.default = default
    opts.strict = strict
    opts.cast = cast

    return opts


class FieldOptions:
    """Represents the options applied to a field using the `dynamicpy.field` function."""

    def __init__(self) -> None:
        self.cast: Union[Callable, None]
        self.default: Any
        self.strict: bool


class FieldMetadata:
    """Represents all of a field's metadata, created when the subclass is defined."""

    def __init__(
        self,
        name: str,
        owner: Type,
        annotation: Type,
        opts: FieldOptions,
    ) -> None:
        self.name: str = name
        self.owner: Type = owner
        self.annotation = annotation
        self.options: FieldOptions = opts

    @property
    def qualname(self) -> str:
        return f"{self.owner.__name__}.{self.name}"

    def get(self, values: Dict[str, Any]) -> Any:
        """Extract, validate, and transform the value for this field from the provided `values` dictionary.

        Parameters
        ----------
        values : Dict[str, Any]
            The dictionary to get values from.

        Returns
        -------
        Any
            The processed value this field should be set to.

        Raises
        ------
        TypeError
            Thrown if the found value is not assignable to this field.
        """
        value = values.get(self.name, self.options.default)

        try:
            check_type(value, self.annotation)
        except TypeCheckError as e:
            factory = self.get_factory()
            if isinstance(value, dict) and factory is not None:
                value = factory(value)
            elif self.options.cast is not None:
                value = self.options.cast(value)
            elif not self.options.strict:
                raise TypeError(
                    f"Value of type {type(value)} is not assignable to field '{self.qualname}'"
                ) from e
        return value

    def get_factory(self) -> Optional[Callable]:
        """Fetches the `from_dict` function of this field's annotaion.

        Returns
        -------
        Optional[Callable]
            The factory function, `None` if no function was found.

        Raises
        ------
        TypeError
            Raised if there were multiple factory functions found.
        """
        if typing.get_origin(self.annotation) is Union:
            types = typing.get_args(self.annotation)
        else:
            types = (self.annotation,)

        factories = {getattr(t, "from_dict") for t in types if hasattr(t, "from_dict")}
        if len(factories) > 1:
            raise TypeError(f"Multiple options for loading '{self.qualname}'")
        return next(iter(factories), None)

    def __get__(self, *_):
        raise AttributeError("Cannot access attributes of non-instance models")


class ModelMeta(ABCMeta):
    """Metaclass for turning `FieldOptions` into `FieldMetadata`."""

    def __init__(self, *args) -> None:
        super().__init__(*args)
        self._fields: List[FieldMetadata] = []
        self._process_fields()

    def _process_fields(self) -> None:
        """Populate fields with `FieldMetadata` instances."""
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
            metadata = FieldMetadata(name, self, resolved, opts)
            self._fields.append(metadata)
            setattr(self, name, metadata)


class Model(Mapping[str, Any], metaclass=ModelMeta):
    """Base class for models to inherit from.

    ## Example:
    ```py
    from dynamicpy import Model

    class User(Model):
        gid: int
        name: str
        avatar: str

    User(guid=123, name="John Doe", avatar="https://bit.ly/3J73JHU")
    ```
    """

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
            setattr(self, field.name, field.get(values))

    @classmethod
    def from_dict(cls, values: Dict[str, Any]) -> Self:
        """Construct an instance of this model from a dictionary.

        Parameters
        ----------
        values : Dict[str, Any]
            The dictionary to get values from.

        Returns
        -------
        Self
            The generated instance.
        """
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
