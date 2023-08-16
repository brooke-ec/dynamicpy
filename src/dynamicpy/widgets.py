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
    def __init__(self, callback: T) -> None:
        self._callback = callback

    @staticmethod
    def get_associations(obj: Any, *, create: bool = True) -> list[BaseWidget]:
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

    @functionify
    def _generate_decorator() -> WidgetDecorator[P, T]:
        def wrapper(cls: Type[BaseWidget], *args, **kwargs) -> Callable[[T], T]:
            def decorator(func: T) -> T:
                cls.associate(func, *args, **kwargs)
                return func

            return decorator

        return wrapper  # type: ignore

    decorate = classmethod(_generate_decorator())

    @property
    def callback(self) -> T:
        return self._callback
