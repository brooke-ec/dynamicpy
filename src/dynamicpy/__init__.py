"""
A python module for dynamically interacting with objects to improve expandability.

https://github.com/NimajnebEC/dynamicpy
"""

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
from dynamicpy.utils import (
    get_foreign_module,
    get_module_parent,
    is_package,
    get_module,
    get_stack_module_up,
)

__all__ = (
    "DynamicLoader",
    "DependencyLibrary",
    "DynamicPyError",
    "NoForeignModulesError",
    "NoParentError",
    "get_foreign_module",
    "get_module_parent",
    "get_stack_module_up",
    "get_module",
    "is_package",
    "DependencyNotFoundError",
    "DuplicateDependencyError",
    "InjectDependenciesError",
)
