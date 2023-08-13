from __future__ import annotations

from typing import Any, Callable, Generic, Type, TypeVar

from typing_extensions import Concatenate, ParamSpec

from dynamicpy.utils import ConstructorProtocol, functionify

__all__ = ("BaseWidget",)

T = TypeVar("T", bound=Callable)
P = ParamSpec("P")

WidgetDecorator = Callable[
    Concatenate[Type[ConstructorProtocol[Concatenate[Any, P]]], P],
    Callable[[T], T],
]


class BaseWidget(Generic[T]):
    def __init__(self, callback: T) -> None:
        self._callback = callback

    @functionify
    def _generate_decorator() -> WidgetDecorator[P, T]:
        def wrapper(cls: Type[BaseWidget], *args, **kwargs) -> Callable[[T], T]:
            def decorator(func: T) -> T:
                return func

            return decorator

        return wrapper  # type: ignore

    decorate = classmethod(_generate_decorator())

    @property
    def callback(self) -> T:
        return self._callback
