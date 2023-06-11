"""
A python module for dynamically importing modules to improve expandability.

https://github.com/NimajnebEC/dynamicpy
"""

from dynamicpy.utils import get_foreign_module, get_module_parent, is_package
from dynamicpy.dependencies import DependencyLibrary
from dynamicpy.loader import DynamicLoader
from dynamicpy.errors import (
    DynamicPyError,
    NoForeignModulesError,
    NoParentError,
    DependencyNotFoundError,
    DuplicateDependencyError,
    InjectDependenciesError,
)

__all__ = (
    "DynamicLoader",
    "DependencyLibrary",
    "DynamicPyError",
    "NoForeignModulesError",
    "NoParentError",
    "get_foreign_module",
    "get_module_parent",
    "is_package",
    "DependencyNotFoundError",
    "DuplicateDependencyError",
    "InjectDependenciesError",
)
