import importlib
import importlib.abc
import importlib.machinery
import importlib.util
import pkgutil
import sys
from types import ModuleType
from typing import Any, Callable, Generic, Iterator, Protocol, Type, TypeVar, Union

from typing_extensions import ParamSpec

import dynamicpy.errors as errors

__all__ = (
    "iter_stack_modules",
    "iter_submodules",
    "get_stack_module_up",
    "get_foreign_module",
    "get_module_parent",
    "is_package",
    "get_module",
    "ConstructorProtocol",
    "functionify",
)

P = ParamSpec("P")
T = TypeVar("T")


def iter_stack_modules(offset: int = 1) -> Iterator[str]:
    """Yields the containing module name for every frame in the stack.

    Parameters
    ----------
    offset : int
        Offset up the stack to start iterating from.

    Yields
    ------
    str
        The name of the frame's containing module.
    """
    frame = sys._getframe(offset)
    while frame is not None:
        yield frame.f_globals.get("__name__", "")
        frame = frame.f_back


def get_stack_module_up(amount: int) -> str:
    """Get the module name of the frame `amount` steps up the stack.

    If `amount` = 0 then the name of the module this function is called from will be returned.

    Parameters
    ----------
    amount : int
        Number of steps up stack to get the module name of.

    Returns
    -------
    str
        The module name of the frame.
    """
    return next(iter_stack_modules(amount + 2))


def get_foreign_module(just_module: bool = False) -> str:
    """Gets the name of the first module with a different top-level package found in the stack.

    Parameters
    ----------
    just_module : bool, optional
        If `True` will also look for sibling modules in the same package, `False` by default.

    Returns
    -------
    str
        The name of the foreign module.

    Raises
    ------
    NoForeignModulesError
        Raised when no foreign module could be found.
    """
    # get module name of caller
    location = get_stack_module_up(1)
    if not just_module:
        location = location.split(".")[0]

    # iterate through stack unil foreign module found
    for module in iter_stack_modules(2):
        if module != location and (just_module or not module.startswith(location + ".")):
            return module
    raise errors.NoForeignModulesError("Could not find any foreign modules in the stack.")


def iter_submodules(package: ModuleType) -> Iterator[importlib.machinery.ModuleSpec]:
    """Yields ModuleSpec for all submodules of the provided package.

    Parameters
    ----------
    module : ModuleType
        The package to iterate through.

    Yields
    ------
    ModuleSpec
        The spec for a submodule of the package.

    Raises
    ------
    ExpectedPackageError
        Raised when the provided module is not a package.
    """
    if not is_package(package):
        raise errors.NotPackageError("Provided module is not a package.")
    for finder, name, _ in pkgutil.iter_modules(package.__path__, package.__name__ + "."):
        spec = None
        if isinstance(finder, importlib.abc.MetaPathFinder):
            spec = finder.find_spec(name, package.__path__)
        elif isinstance(finder, importlib.abc.PathEntryFinder):
            spec = finder.find_spec(name, package)

        if spec is not None:
            yield spec


def is_package(module: Union[str, ModuleType]) -> bool:
    """Checks if the given module is a package.

    Parameters
    ----------
    module : ModuleType
        The module to check.

    Returns
    -------
    bool
        True if the provided module is a package.
    """
    if isinstance(module, str):
        module = get_module(module)
    return hasattr(module, "__path__")


def get_module(name: str, package: Union[str, ModuleType, None] = None) -> ModuleType:
    """Gets a module from its name.

    Parameters
    ----------
    name : str
        The absolute name of the module.
    package : Union[str, ModuleType], optional
        If present, will perform a relative import from the specified package.

    Returns
    -------
    ModuleType
        The imported module.

    Raises
    ------
    ImportError
        Raised when there is an error importing the module.
    """
    if isinstance(package, ModuleType):
        package = package.__name__
    return importlib.import_module(name, package)


def get_module_parent(module: Union[ModuleType, str]) -> str:
    """Gets the parent package of the specified module.

    Parameters
    ----------
    module : str
        The module to get the parent of.

    Returns
    -------
    str
        The parent package of the specified module.

    Raises
    ------
    NoParentError
        Raised when the specified module has no parent.
    """
    if isinstance(module, ModuleType):
        module = module.__name__
    try:
        resolved = importlib.util.resolve_name("..", module)
    except ImportError:
        raise errors.NoParentError(f"'{module}' does not have a parent.")
    return resolved


class _functionify(staticmethod, Generic[P, T]):
    def __init__(self, func: Callable[P, T]) -> None:
        super().__init__(func)
        self.func = func

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        return self.func(*args, **kwds)  # type: ignore


functionify: Type[staticmethod] = _functionify
"""A callable version of the `staticmethod` decorator."""


class ConstructorProtocol(Protocol[P]):
    """A protocol to retrieve a class' constructor parameters into the `ParamSpec`, `P`"""

    __init__: Callable[P, None]
