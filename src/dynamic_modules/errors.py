__all__ = (
    "DynamicModulesError",
    "NoEligibleModulesError",
    "ExpectedPackageError",
    "NoParentError",
)


class DynamicModulesError(Exception):
    """Base exception class for the dynamic modules module."""


class NoEligibleModulesError(Exception):
    """Raised when no eligible modules are found from the `traverse_stack` function."""


class ExpectedPackageError(DynamicModulesError):
    """Exception raised when function expected a package but got a module."""


class NoParentError(DynamicModulesError):
    """Exception raised when trying to get the parent of a top level module."""
