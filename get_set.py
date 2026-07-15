# SPDX-FileCopyrightText: 2025 Authors (see AUTHORS file)
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Getters and setters for settings.

This module implements the synchronization between the addon preferences and
the input file exported to BlendLuxCore.
"""

_needs_reload = "bpy" in locals()

import json
import pathlib

import bpy

from . import utils

if _needs_reload:
    import importlib

    utils = importlib.reload(utils)


SETTINGS_FILENAME = "blc_settings.json"
SETTINGS_INIT = {
    "wheel_source": 0,
    "wheel_version": "",
    "path_to_wheel": "",
    "path_to_wheel_deps": "",
    "path_to_folder": "",
    "reinstall_upon_reloading": False,
    "no_deps": False,
    "no_index": False,
}


def get_settings_file_path():
    """Path to settings file."""
    settings_folder = pathlib.Path(
        bpy.utils.user_resource("CONFIG", path="blendluxcore", create=True)
    )
    settings_file = settings_folder / SETTINGS_FILENAME
    return settings_file


def _get_settings():
    """Get settings dictionary from json file.

    Create json file if it does not exist and (re)initialize it if needed.
    If settings file path is not known (BlendLuxCore not installed), return
    internal dictionary.
    """
    if not (settings_file := get_settings_file_path()):
        raise RuntimeError("Missing BlendLuxCore")

    settings_file.touch(exist_ok=True)
    try:
        with open(settings_file, "r", encoding="utf-8") as fsettings:
            return json.load(fsettings)
    except json.JSONDecodeError:
        with open(settings_file, "w", encoding="utf-8") as fsettings:
            # (Re)init settings file
            json.dump(SETTINGS_INIT, fsettings)
        return _get_settings()


def _set_settings(settings):
    """Write settings in json file."""
    if not (settings_file := get_settings_file_path()):
        raise RuntimeError("Missing BlendLuxCore")
    settings_file = get_settings_file_path()
    with open(settings_file, "w", encoding="utf-8") as fsettings:
        json.dump(settings, fsettings)


def _get(setting):
    """Read a given setting."""
    settings = _get_settings()
    return settings[setting]


def _set(setting, value):
    """Set a given setting."""
    settings = _get_settings()
    settings[setting] = value
    _set_settings(settings)


def get_wheel_source(_):
    """Getter for wheel source preference."""
    return _get("wheel_source")


def set_wheel_source(_, value):
    """Setter for wheel source preference."""
    _set("wheel_source", value)


def get_wheel_version(_):
    """Getter for wheel version preference."""
    return _get("wheel_version")


def set_wheel_version(_, value):
    """Setter for wheel version preference."""
    _set("wheel_version", value)


def get_path_to_wheel(_):
    """Getter for path to wheel preference."""
    return _get("path_to_wheel")


def set_path_to_wheel(_, value):
    """Setter for path to wheel preference."""
    _set("path_to_wheel", value)


def get_path_to_folder(_):
    """Getter for path to folder preference."""
    return _get("path_to_folder")


def set_path_to_folder(_, value):
    """Setter for path to folder preference."""
    _set("path_to_folder", value)


def get_reinstall_upon_reloading(_):
    """Getter for 'reinstall upon reloading' preference."""
    return _get("reinstall_upon_reloading")


def set_reinstall_upon_reloading(_, value):
    """Setter for 'reinstall upon reloading' preference."""
    _set("reinstall_upon_reloading", value)


def get_no_deps(_):
    """Getter for 'no deps' preference."""
    return _get("no_deps")


def set_no_deps(_, value):
    """Setter for 'no deps' preference."""
    _set("no_deps", value)


def get_no_index(_):
    """Getter for 'no index' preference."""
    return _get("no_index")


def set_no_index(_, value):
    """Setter for 'no index' preference."""
    _set("no_index", value)


def get_path_to_wheel_deps(_):
    """Getter for 'path to wheel deps' preference."""
    return _get("path_to_wheel_deps")


def set_path_to_wheel_deps(_, value):
    """Setter for 'path to wheel deps' preference."""
    _set("path_to_wheel_deps", value)
