# coding: utf8

__all__ = ["scan_package", "scan_path"]
__authors__ = ["Tim Chow"]

from pkgutil import iter_modules
import importlib
import os


def __scan_package(base_package):
    mods = []
    mod = importlib.import_module(base_package)
    mods.append(mod)

    if not hasattr(mod, "__path__"):
        return mods

    for importer, name, is_pkg in iter_modules(mod.__path__):
        full_name = base_package + "." + name
        if is_pkg:
            mods.extend(__scan_package(full_name))
            continue
        mod = importer.find_module(full_name).load_module(full_name)
        mods.append(mod)
    return mods


def scan_package(*base_packages):
    mods = set()
    for base_package in base_packages:
        mods.update(__scan_package(base_package))
    return mods


def __scan_path(base_path, base_package_name=None):
    mods = set()
    for importer, name, is_pkg in iter_modules([base_path]):
        full_name = base_package_name and \
            (base_package_name + "." + name) or name
        mod = importer.find_module(full_name).load_module(full_name)
        mods.add(mod)
        if is_pkg:
            mods.update(__scan_path(
                os.path.join(base_path, name),
                full_name))
    return mods


def scan_path(*paths):
    mods = set()
    for path in paths:
        mods.update(__scan_path(path))
    return mods
