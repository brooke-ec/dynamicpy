"""
A python module for dynamically importing modules to improve expandability.

https://github.com/NimajnebEC/dynamicpy
"""
from dynamicpy.errors import DynamicModulesError, NoForeignModulesError, NoParentError
from dynamicpy.utils import get_foreign_module, get_module_parent
from dynamicpy.loader import DynamicLoader

__all__ = (
    "DynamicLoader",
    "DynamicModulesError",
    "NoForeignModulesError",
    "NoParentError",
    "get_foreign_module",
    "get_module_parent",
)
