__all__ = (
    "DynamicModulesError",
    "NotPackageError",
    "NoParentError",
    "DuplicateDependencyError",
    "DependencyNotFoundError",
)


class DynamicModulesError(Exception):
    """Base exception class for the dynamic modules module."""


class NoForeignModulesError(DynamicModulesError):
    """Exception raised when no foreign modules could be found."""


class NotPackageError(DynamicModulesError):
    """Exception raised when function expected a package but got a module."""


class NoParentError(DynamicModulesError):
    """Exception raised when trying to get the parent of a top level module."""


class DuplicateDependencyError(DynamicModulesError):
    """Exception raised when trying to add a dependency to a `DependencyLibrary` which already has a dependency of that type."""


class DependencyNotFoundError(DynamicModulesError):
    """Exception raised when no dependency could be find in the `DependencyLibrary` of that type."""
