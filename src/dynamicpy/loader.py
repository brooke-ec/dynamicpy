from typing import Union, Optional, Callable
from types import ModuleType
from dynamicpy import utils
import logging

__all__ = ("DynamicLoader",)

_log = logging.getLogger(__name__)

Handler = Callable[[str, object], None]

Selector = Callable[[str, object], bool]


class DynamicLoader:
    # TODO: Add docstring

    def __init__(self) -> None:
        self._handlers: list[_SelectorHandlerPair] = []

    def register_handler(self, handler: Handler, selector: Optional[Selector] = None):
        """Register a handler for the specified selector.

        Parameters
        ----------
        handler : Callable[[str, object], None]
            The handler to be called if the predicate returns `True`.
        selector : Callable[[str, object], bool], optional
            A predicate that will be run against every global. If `True` is returned then the global passed to the handler.
        """
        selector = selector or (lambda x, y: True)
        self._handlers.append(_SelectorHandlerPair(selector, handler))

    def register(self, selector: Optional[Selector] = None):
        """A wrapper around around the `register_handler` function to be used as a decorator.

        Parameters
        ----------
        selector : Selector
            A predicate that will be run against every global. If `True` is returned then the global passed to the handler.
        """

        def decorator(handler: Handler):
            self.register_handler(handler, selector)

        return decorator

    def search_module(
        self,
        path: str,
        package: Optional[str] = None,
        recursion_depth: Optional[int] = None,
    ) -> None:
        """Recursively search the specified module.

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
        """  # TODO: Improve Summary
        module = utils.get_module(path, package)
        self._search_module(module, recursion_depth)

    def _search_module(self, module: ModuleType, recursion_depth: Union[int, None]):
        _log.debug("Searching module '%s'", module.__name__)

        # Recursively Search Submodules
        infinite = recursion_depth is None
        if (infinite or recursion_depth > 0) and utils.is_package(module):
            for spec in utils.iter_submodules(module):
                # Ignore Private Modules
                if spec.name.startswith("_"):
                    continue

                # Import and Search Submodule
                submodule = utils.get_module(spec.name)
                self._search_module(submodule, None if infinite else recursion_depth - 1)

        # Search Globals
        for name, value in vars(module).items():
            # Ignore Private and Built-In Attributes
            if name.startswith("_"):
                continue

            # Iterate through handlers
            for handler in self._handlers:
                handler.handle(name, value)


class _SelectorHandlerPair:
    def __init__(self, selector: Selector, handler: Handler) -> None:
        self.selector = selector
        self.handler = handler

    def handle(self, name: str, value: object):
        # Run handler if selector applies to global
        if self.selector(name, value):
            self.handler(name, value)
