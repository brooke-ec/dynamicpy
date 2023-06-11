from typing import Union, TypeVar, Type, Callable
from typeguard import check_type, TypeCheckError
from dynamicpy import errors
import inspect
import logging

__all__ = ("DependencyLibrary",)

_log = logging.getLogger(__name__)

T = TypeVar("T")


class DependencyLibrary:
    """An instance of `DependencyLibrary` can be used to build up a library of objects that can be injected into functions by type."""

    def __init__(self) -> None:
        """An instance of `DependencyLibrary` can be used to build up a library of objects that can be injected into functions by type."""
        self._library: list[object] = []

    def add(self, dependency: object):
        """Adds a dependency to the library.

        Parameters
        ----------
        dependency : object
            The dependency to add to the library,

        Raises
        ------
        TypeError
            Raised when attempting to add a type to the library.
        DuplicateDependencyError
            Raised when another dependency with that type already exists in the library.
        """
        if isinstance(dependency, type):
            raise TypeError("Dependencies cannot be types.")
        if type(dependency) in self:
            raise errors.DuplicateDependencyError(
                f"Instance of '{type(dependency)}' already in library."
            )
        self._library.append(dependency)

    def inject(self, func: Callable[..., T]) -> T:
        """Calls the specified function, injecting dependencies from the library into parameters by type annotations.

        Parameters
        ----------
        func : Callable
            The function to call.

        Returns
        -------
            The return value of the `func` parameter.

        Raises
        ------
        InjectDependenciesError
            Raised when there is an error injecting dependencies.
        DependencyNotFoundError
            Raised when a requested dependency could not be found.
        """
        signature = inspect.signature(func)

        args = []
        kwargs = {}
        # Iterate through function parameters
        for parameter in signature.parameters.values():
            try:
                # Attempt to find dependency in library
                value = self[parameter.annotation]
            except errors.DependencyNotFoundError:
                # Ignore missing dependency if parameter has default value
                if parameter.default is inspect._empty:
                    raise
                continue
            # Add value to the appropriate collection
            if parameter.kind is parameter.POSITIONAL_ONLY:
                args.append(value)
            else:
                kwargs[parameter.name] = value

        try:
            # Attempt to bind parameters
            signature.bind(*args, **kwargs)
        except TypeError as e:
            raise errors.InjectDependenciesError(
                "Could not bind dependencies to function."
            ) from e

        return func(*args, **kwargs)

    def __contains__(self, item: Union[type, object]) -> bool:
        if isinstance(item, type):
            try:
                self[type]
            except errors.DependencyNotFoundError:
                return False
            else:
                return True
        else:
            return item in self._library

    def __getitem__(self, type: Type[T]) -> T:
        for dependency in self._library:
            try:
                return check_type(dependency, type)
            except TypeCheckError:
                continue
        raise errors.DependencyNotFoundError(f"No dependency of type '{type}' found.")
