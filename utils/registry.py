# src/SPHENDR/utils/registry.py
import pkgutil
import importlib
import os
PROCESSOR_REGISTRY = {}

def register_processor(name):
    def decorator(cls):
        PROCESSOR_REGISTRY[name] = cls
        return cls
    return decorator
def load_all_processors():

    path = os.path.dirname(__file__)
    for _, name, _ in pkgutil.iter_modules([path]):

        importlib.import_module(f"SPHENDR.utils.{name}")