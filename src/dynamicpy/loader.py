from typing import Union, Optional
from dynamicpy import utils
from types import ModuleType

__all__ = ("DynamicLoader",)


class DynamicLoader:
    # TODO: Add docstring

    def __init__(self) -> None:
        pass

    def search_module(
        self,
        path: str,
        package: Optional[str] = None,
        recursion_depth: Optional[int] = None,
    ) -> None:
        """Recursively search the specified module.

        Parameters
        ----------
        path : str
            The name of the module to search.
        package : str, optional
            If present, will perform a relative import from the specified package.
        recursion_depth : int, optional
            The number of layers to look for submodules. Is `None` by default and has no maximum depth.

        Raises
        ------
        ImportError
            Raised when there is an error importing a module.
        """  # TODO: Improve Summary
        module = utils.get_module(path, package)
        self._search_module(module, recursion_depth)

    def _search_module(self, module: ModuleType, recursion_depth: Union[int, None]):
        # Recursively Search Submodules
        infinite = recursion_depth is None
        if (infinite or recursion_depth > 0) and utils.is_package(module):
            for spec in utils.iter_submodules(module):
                # Ignore Private Modules
                if spec.name.startswith("_"):
                    continue

                # Import and Search Submodule
                submodule = utils.get_module(spec.name)
                self._search_module(submodule, None if infinite else recursion_depth - 1)

        # Search Globals
        for name, value in vars(module).items():
            # Ignore Private and Built-In Attributes
            if name.startswith("_"):
                continue

            print(name, type(value))
