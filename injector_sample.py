"""
Core concept of the injector module:
- Injector: This is the container that manages and injects dependencies
- Module:   A place where you configure the bindings between interfaces (abstract classes and types) and their implementation 
- Binding:  Mapping a type to its implementation; controlling how dependencies are provided.
- Injection Decorator(@inject):
            Marks a class or method to indicate that dependencies will be injected by Injector.
"""
from injector import inject, Module, singleton, Binder, Injector
# Define the Dependencies
# engine.py
class Engine:
    def start(self):
        print("Engine start")


class ElectricEngine(Engine):
    def start(self):
        print("Electric Engine started silently")


# Create the Dependent Class
class Car:
    @inject
    def __init__(self, engine: Engine):
        self.engine = engine

    def start(self):
        self.engine.start()


# Configure Binding Using a Module
# To allow the Injector to know which implementation to use for Engine, we use a module to configure the binding.
class EVModule(Module):
    def configure(self, binder: Binder):
        binder.bind(Engine, to=ElectricEngine, scope=singleton)


class ICEModule(Module):
    def configure(self, binder: Binder):
        binder.bind(Engine, to=Engine, scope=singleton)
        

# Set up the Injector
# Use the Injector class to get a fully configured Car instance 
# Create an injector and provide the module for bindings
ev_injector = Injector([EVModule])
ice_injector = Injector([ICEModule])

# Retrieve and instance of Car with dependencies injected
ev_car = ev_injector.get(Car)
ev_car.start()

ice_car = ice_injector.get(Car)
ice_car.start()

"""
Dependency Injection is a set of software design principles and patterns that enables you to develop loosely coupled code.

In DI terminology, we often talk about services and components. A service is typically an ABSTRACTION, a definition for something that 
provides a service. An implementation of an ABSTRACTION is often called a component a class that contains behavior. Because both service
and component are such overloaded terms, throughout this book, you will typically see us use the terms "ABSTRACTION" and "class" instead.


"""