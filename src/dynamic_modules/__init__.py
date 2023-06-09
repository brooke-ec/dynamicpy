"""
A python module for dynamically importing modules to improve expandability.

https://github.com/NimajnebEC/dynamic-modules
"""

from dynamic_modules.errors import DynamicModulesError, NoForeignModulesError, NoParentError
from dynamic_modules.utils import get_foreign_module, get_module_parent
from dynamic_modules.loader import DynamicLoader

__all__ = (
    "DynamicLoader",
    "DynamicModulesError",
    "NoForeignModulesError",
    "NoParentError",
    "get_foreign_module",
    "get_module_parent",
)
