# DynamicPy

A python module for dynamically interacting with objects to improve expandability.

## DynamicLoader

The `DynamicLoader` class allows for the dynamic import of modules and the scraping of their globals.

To provide functionality with the scraped globals you must register a handler using the `register_handler` method or the `handler` decorator. Both methods take an optional `selector` parameter which is a predicate to determine wether the handler should be called.

### Example:

```py
from dynamicpy import DynamicLoader

loader = DynamicLoader()

@loader.handler()
def handler(name: str, value: object):
    print(name) # Prints the name of every global imported

loader.load_module("package.module")
```

Dynamicpy provides a handful of utility functions to traverse modules in the stack which can be useful for streamlining this process.

## DependencyLibrary

The `DependencyLibrary` class allows you to create a library of objects which can then be injected into function parameters using type annotations.

Dependencies are added using the `add` method, only a single dependency per type can be added to the library. Dependencies can be retrived using square brackets. You can check if an object has been added to the library using the `in` operator which can also be used to check if there are any dependencies of a certain type in the library.

### Example

```py
from dynamicpy import DependencyLibrary

library = DependencyLibrary()
library.add("Hello World!")

print(library[str]) # Hello World!

print(str in library) # True
print("Hello World!" in library) # True
print("Lorem Ipsum" in library) # False
print(int in library) # False
```

The `DependencyLibrary` class also allows for dependencies to be injected into function parameters using the `inject` method.

### Example

```py
from dynamicpy import DependencyLibrary

library = DependencyLibrary()
library.add("Hello World!")

def injected(message: str):
    print(message) # Hello World!

library.inject(injected)
```
