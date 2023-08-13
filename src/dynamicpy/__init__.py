"""
A python module for dynamically interacting with objects to improve expandability.

https://github.com/NimajnebEC/dynamicpy
"""

from dynamicpy.dependencies import DependencyLibrary
from dynamicpy.errors import (
    DependencyNotFoundError,
    DuplicateDependencyError,
    DynamicPyError,
    InjectDependenciesError,
    NoForeignModulesError,
    NoParentError,
)
from dynamicpy.loader import DynamicLoader
from dynamicpy.utils import (
    ConstructorProtocol,
    functionify,
    get_foreign_module,
    get_module,
    get_module_parent,
    get_stack_module_up,
    is_package,
)
from dynamicpy.widgets import BaseWidget

__all__ = (
    "DynamicLoader",
    "DependencyLibrary",
    "DynamicPyError",
    "NoForeignModulesError",
    "NoParentError",
    "ConstructorProtocol",
    "functionify",
    "get_foreign_module",
    "get_module_parent",
    "get_stack_module_up",
    "get_module",
    "is_package",
    "DependencyNotFoundError",
    "DuplicateDependencyError",
    "InjectDependenciesError",
    "BaseWidget",
)
