__all__ = (
    "DynamicModulesError",
    "NotPackageError",
    "NoParentError",
)


class DynamicModulesError(Exception):
    """Base exception class for the dynamic modules module."""


class NoForeignModulesError(DynamicModulesError):
    """Exception raised when no foreign modules could be found."""


class NotPackageError(DynamicModulesError):
    """Exception raised when function expected a package but got a module."""


class NoParentError(DynamicModulesError):
    """Exception raised when trying to get the parent of a top level module."""
