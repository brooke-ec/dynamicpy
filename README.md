# DynamicPy <!-- omit from toc -->

A python module for dynamically interacting with objects to improve expandability.

### Features

- [Dynamic Loader](#dynamic-loader)
- [Dependency Library](#dependency-library)
- [Widgets](#widgets)
- [Models](#models)

## Dynamic Loader

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

DynamicPy provides a handful of utility functions to traverse modules in the stack which can be useful for streamlining this process.

## Dependency Library

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

## Widgets

DynamicPy contains a helper for making 'widgets' with callback functions which are created using a decorator. Configure your widget by extending the `BaseWidget` class. Set the type parameter to configure the expected callback type.

```py
from typing import Any, Callable
from dynamicpy import BaseWidget

class ExampleWidget(BaseWidget[Callable[[str], Any]]):
    def __init__(self, callback: Callable[[str], Any], enabled: bool) -> None:
        super().__init__(callback)
```

DynamicPy will automatically generate a `BaseWidget.decorate` function based off your constructor.

```py
@ExampleWidget.decorate(enabled=False)
def example(message: str):
    print(message)
```

This will add an attribute to the function, containing an instance of your widget. This can be easily retrieved using a [Dynamic Loader](#dynamic-loader)'s `register_widget_handler` method or `widget_handler` decorator.

```py
from dynamicpy import DynamicLoader

loader = DynamicLoader()

@loader.widget_handler(ExampleWidget)
def widget_handler(widget: ExampleWidget):
    widget.callback("Hello World!")  # prints "Hello World!"
```

## Models

DynamicPy provides its own system similar to [dataclasses](https://docs.python.org/3/library/dataclasses.html) called models which are designed to aid in data validation and type hinting. A model can be defined by simply extending the `dynamicpy.Model` class and specifying fields. These fields can be populated using the model's constructor.

```py
from dynamicpy import Model

class User(Model):
    gid: int
    name: str
    avatar: str

User(guid=123, name="John Doe", avatar="https://bit.ly/3J73JHU")
```

Behaviour can be further configured using the `dynamicpy.field` function.

```py
from dynamicpy import Model, field

class User(Model):
    gid: int = field(cast=int)
    name: str = field(default="Unnamed")
    avatar: str = "https://bit.ly/3J73JHU" # default alternative

User(guid="123")
```

Models will also recursively load types with a `from_dict` classmethod (including other models).

```py
from dynamicpy import Model

class User(Model):
    gid: int
    name: str

class Post(Model):
    title: str
    author: User

Post.from_dict({"title": "Lorem Ipsum", "author": {"gid": 123, "name": "John Doe"}})
```
