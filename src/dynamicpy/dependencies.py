from typing import Union, TypeVar, Type
from dynamicpy import errors

__all__ = ("DependencyLibrary",)

T = TypeVar("T")


class DependencyLibrary:
    """An instance of `DependencyLibrary` can be used to build up a library of objects that can be injected into functions."""

    def __init__(self) -> None:
        """An instance of `DependencyLibrary` can be used to build up a library of objects that can be injected into functions."""
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
            if isinstance(dependency, type):
                return dependency
        raise errors.DependencyNotFoundError(f"No dependency of type '{type}' found.")
