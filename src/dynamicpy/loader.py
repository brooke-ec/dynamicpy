import logging
from types import ModuleType
from typing import Any, Callable, Optional, Type, TypeVar, Union

from typeguard import TypeCheckError, check_type

from dynamicpy import utils

__all__ = ("DynamicLoader",)

_log = logging.getLogger(__name__)

T = TypeVar("T")
Handler = Callable[[str, T], None]
Selector = Callable[[str, object], bool]


class DynamicLoader:
    """An instance of `DynamicLoader` can be used to dynamically import modules and handle their attributes through registered handlers."""

    def __init__(self) -> None:
        """An instance of `DynamicLoader` can be used to dynamically import modules and handle their attributes through registered handlers."""
        self._handlers: list[_SelectorHandlerPair] = []

    def register_handler(self, handler: Handler[Any], selector: Optional[Selector] = None):
        """Register a handler for the specified selector.

        Parameters
        ----------
        handler : Callable[[str, object], None]
            The handler to be called if the predicate returns `True`.
        selector : Callable[[str, object], bool], optional
            A predicate that will be run against every attribute. If `True` is returned then the atribute passed to the handler.
        """
        selector = selector or (lambda x, y: True)
        self._handlers.append(_SelectorHandlerPair(selector, handler))

    def handler(
        self, selector: Optional[Selector] = None
    ) -> Callable[[Handler[Any]], None]:
        """A wrapper around around the `register_handler` function to be used as a decorator.

        Parameters
        ----------
        selector : Selector
            A predicate that will be run against every attribute. If `True` is returned then the atribute passed to the handler.
        """

        def decorator(handler: Handler[Any]) -> None:
            self.register_handler(handler, selector)

        return decorator

    def register_type_handler(self, handler: Handler[T], type: Type[T]):
        """Register a handler that matches for the specified type.

        Parameters
        ----------
        handler : Callable[[str, object], None]
            The handler to be called if the attribute matches the specified type.
        type : Type
            The type to match against.
        """

        def selector(_, value: object):
            try:
                check_type(value, type)
            except TypeCheckError:
                return False
            else:
                return True

        self.register_handler(handler, selector)

    def type_handler(self, type: Type[T]) -> Callable[[Handler[T]], None]:
        """A wrapper around around the `register_type_handler` function to be used as a decorator.

        Parameters
        ----------
        type : Type
            The type to run the handler on if an assignable attribute is found.
        """

        def decorator(handler: Handler[T]) -> None:
            self.register_type_handler(handler, type)

        return decorator

    def load_object(self, object: object) -> None:
        """Handle the attributes of the specified object with registered handlers.

        Parameters
        ----------
        object : object
            The object to load.
        """
        for name, value in vars(object).items():
            # Ignore Private and Built-In Attributes
            if name.startswith("_"):
                continue

            # Iterate through handlers
            for handler in self._handlers:
                handler.handle(name, value)

    def load_module(
        self,
        path: str,
        package: Optional[str] = None,
        recursion_depth: Optional[int] = None,
    ) -> None:
        """Recursively load the specified module and submodules and handle globals with registered handlers.

        Parameters
        ----------
        path : str
            The name of the module to search.
        package : str, optional
            If present, will perform a relative import from the specified package.
        recursion_depth : int, optional
            The number of layers to look for submodules. Is `None` by default and has no maximum depth.

        Raises
        ------
        ImportError
            Raised when there is an error importing a module.
        """
        module = utils.get_module(path, package)
        self._load_module(module, recursion_depth)

    def _load_module(self, module: ModuleType, recursion_depth: Union[int, None]):
        _log.debug("Searching module '%s'", module.__name__)

        # Recursively Load Submodules
        infinite = recursion_depth is None
        if (infinite or recursion_depth > 0) and utils.is_package(module):
            for spec in utils.iter_submodules(module):
                # Ignore Private Modules
                if spec.name.startswith("_"):
                    continue

                # Import and Load Submodule
                submodule = utils.get_module(spec.name)
                self._load_module(submodule, None if infinite else recursion_depth - 1)

        # Search Globals
        self.load_object(module)


class _SelectorHandlerPair:
    def __init__(self, selector: Selector, handler: Handler) -> None:
        self.selector = selector
        self.handler = handler

    def handle(self, name: str, value: object):
        # Run handler if selector applies to attribute
        if self.selector(name, value):
            self.handler(name, value)
