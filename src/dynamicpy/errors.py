__all__ = (
    "DynamicPyError",
    "NotPackageError",
    "NoParentError",
    "DuplicateDependencyError",
    "DependencyNotFoundError",
)


class DynamicPyError(Exception):
    """Base exception class for the dynamicpy module."""


class NoForeignModulesError(DynamicPyError):
    """Exception raised when no foreign modules could be found."""


class NotPackageError(DynamicPyError):
    """Exception raised when function expected a package but got a module."""


class NoParentError(DynamicPyError):
    """Exception raised when trying to get the parent of a top level module."""


class DuplicateDependencyError(DynamicPyError):
    """Exception raised when trying to add a dependency to a `DependencyLibrary` which already has a dependency of that type."""


class DependencyNotFoundError(DynamicPyError):
    """Exception raised when no dependency could be find in the `DependencyLibrary` of that type."""


class InjectDependenciesError(DynamicPyError):
    """Exception raised when there was an error injecting dependencies into a function."""
