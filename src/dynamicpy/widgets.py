from __future__ import annotations

import contextlib
from abc import ABC
from typing import Any, Callable, Generic, Type, TypeVar

from typing_extensions import Concatenate, ParamSpec

from dynamicpy.loader import DynamicLoader
from dynamicpy.utils import ConstructorProtocol, functionify

__all__ = ("BaseWidget",)

ASSOCIATION_ATTRIBUTE = "_dynamicpy_widgets"

WidgetT = TypeVar("WidgetT", bound="BaseWidget")
T = TypeVar("T", bound=Callable)
P = ParamSpec("P")

WidgetDecorator = Callable[
    Concatenate[Type[ConstructorProtocol[Concatenate[Any, P]]], P],
    Callable[[T], T],
]

WidgetAssociator = Callable[Concatenate[Type[ConstructorProtocol[P]], P], None]

WidgetHandler = Callable[[WidgetT], None]


class BaseWidget(ABC, Generic[T]):
    def __init__(self, callback: T) -> None:
        self._callback = callback

    @staticmethod
    def get_associations(obj: Any, *, create: bool = True) -> list[BaseWidget]:
        if create and not hasattr(obj, ASSOCIATION_ATTRIBUTE):
            setattr(obj, ASSOCIATION_ATTRIBUTE, [])

        return getattr(obj, ASSOCIATION_ATTRIBUTE)  # type: ignore

    @classmethod
    def register_handler(
        cls: Type[WidgetT],
        loader: DynamicLoader,
        handler: WidgetHandler[WidgetT],
    ):
        def wrapper(_, value: Any):
            with contextlib.suppress(AttributeError):
                for widget in cls.get_associations(value, create=False):
                    if isinstance(widget, cls):
                        handler(widget)

        loader.register_handler(wrapper)

    @classmethod
    def handler(
        cls: Type[WidgetT], loader: DynamicLoader
    ) -> Callable[[WidgetHandler[WidgetT]], WidgetHandler[WidgetT]]:
        def decorator(func: WidgetHandler[WidgetT]) -> WidgetHandler[WidgetT]:
            cls.register_handler(loader, func)
            return func

        return decorator

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
