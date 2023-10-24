from __future__ import annotations

from abc import ABC
from typing import Any, Callable, Generic, Type, TypeVar

from typing_extensions import Concatenate, ParamSpec

from dynamicpy.utils import ConstructorProtocol, functionify

__all__ = ("BaseWidget",)

ASSOCIATION_ATTRIBUTE = "_dynamicpy_widgets"

T = TypeVar("T", bound=Callable)
P = ParamSpec("P")

WidgetDecorator = Callable[
    Concatenate[Type[ConstructorProtocol[Concatenate[Any, P]]], P],
    Callable[[T], T],
]

WidgetAssociator = Callable[Concatenate[Type[ConstructorProtocol[P]], P], None]


class BaseWidget(ABC, Generic[T]):
    """Helper class for making 'widgets' with callback functions, created using a constructor."""

    def __init__(self, callback: T) -> None:
        """Helper class for making 'widgets' with callback functions, created using a constructor."""
        self._callback = callback

    @staticmethod
    def get_associations(obj: Callable, *, create: bool = True) -> list[BaseWidget]:
        """Gets the widget associations of the specified function.

        Parameters
        ----------
        obj : Callable
            The function to get the widget associations of.
        create : bool, optional
            Wether to create the associations attribute if it does not exist, by default True

        Returns
        -------
        list[BaseWidget]
            The list of widgets associated with this object.
        """

        if create and not hasattr(obj, ASSOCIATION_ATTRIBUTE):
            setattr(obj, ASSOCIATION_ATTRIBUTE, [])

        return getattr(obj, ASSOCIATION_ATTRIBUTE)  # type: ignore

    @functionify
    def _generate_associator() -> WidgetAssociator[P]:
        def wrapper(cls: Type[BaseWidget], callback: T, *args, **kwargs) -> None:
            ins = cls(callback, *args, **kwargs)
            cls.get_associations(callback).append(ins)

        return wrapper  # type: ignore

    associate = classmethod(_generate_associator())
    """Associate the specified function with this widget.

    Parameters
    ----------
    callback : Callable
        The function to associate this widget with.
    """

    @functionify
    def _generate_decorator() -> WidgetDecorator[P, T]:
        def wrapper(cls: Type[BaseWidget], *args, **kwargs) -> Callable[[T], T]:
            def decorator(func: T) -> T:
                cls.associate(func, *args, **kwargs)
                return func

            return decorator

        return wrapper  # type: ignore

    decorate = classmethod(_generate_decorator())
    """Decorator around the `associate` function."""

    @property
    def callback(self) -> T:
        return self._callback
