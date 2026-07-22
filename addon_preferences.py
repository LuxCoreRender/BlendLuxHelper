# SPDX-FileCopyrightText: 2025 Authors (see AUTHORS file)
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""This module implements the preferences panel of the add-on."""

_needs_reload = "bpy" in locals()

import bpy
import sys
from pathlib import Path

from . import utils
from . import get_set

if _needs_reload:
    import importlib

    utils = importlib.reload(utils)
    get_set = importlib.reload(get_set)

SPLIT_FACTOR = 1 / 3

enum_wheel_sources = (
    ("PyPI", "PyPI", "Get PyLuxCore from Python Package Index (PyPI)", 0),
    (
        "LocalWheel",
        "Local Wheel",
        "Get PyLuxCore from a local wheel file, not including dependencies",
        1,
    ),
)


print(f"[BLH] Declaring Addon Preferences with bl_idname='{__package__}'")


class BLHSettings(bpy.types.AddonPreferences):
    """Addon preferences panel."""

    bl_idname = __package__

    wheel_source: bpy.props.EnumProperty(
        name="Source",
        description="PyLuxCore source",
        items=enum_wheel_sources,
        get=get_set.get_wheel_source,
        set=get_set.set_wheel_source,
    )

    wheel_version: bpy.props.StringProperty(
        name="Wheel version",
        description=(
            "Wheel version, for PyPI.\n"
            "This uses exact matching, with trailing * allowed, as documented here: "
            "https://packaging.python.org/en/latest/specifications"
            "/version-specifiers/#version-matching.\n"
            "Example: 2.10.1"
        ),
        default="",
        get=get_set.get_wheel_version,
        set=get_set.set_wheel_version,
    )

    path_to_wheel: bpy.props.StringProperty(
        name="Path to Wheel",
        description="Path to PyLuxCore Wheel file",
        subtype="FILE_PATH",
        get=get_set.get_path_to_wheel,
        set=get_set.set_path_to_wheel,
    )

    path_to_wheel_deps: bpy.props.StringProperty(
        name="Path to Additional Dependency Folder (optional)",
        description="Path to Additional Wheel Dependency Folder",
        subtype="DIR_PATH",
        get=get_set.get_path_to_wheel_deps,
        set=get_set.set_path_to_wheel_deps,
    )

    reinstall_upon_reloading: bpy.props.BoolProperty(
        name="Reinstall upon each Reloading",
        description="Reinstall every time BlendLuxCore is reloaded",
        get=get_set.get_reinstall_upon_reloading,
        set=get_set.set_reinstall_upon_reloading,
    )

    no_deps: bpy.props.BoolProperty(
        name="No Remote Dependencies",
        description=(
            "Do not load wheel dependencies from remote. "
            "Nota: you will have to provide them in local."
        ),
        get=get_set.get_no_deps,
        set=get_set.set_no_deps,
    )

    no_index: bpy.props.BoolProperty(
        name="No Index",
        description=(
            "Ignore package index.\n"
            "This handles --no-index flag of pip download. See documentation here: "
            "https://pip.pypa.io/en/stable/cli/pip_download/#cmdoption-no-index"
        ),
        get=get_set.get_no_index,
        set=get_set.set_no_index,
    )

    settings_file: bpy.props.StringProperty(
        name="Settings output file (read-only)",
        get=lambda _: str(get_set.get_settings_file_path()),
    )

    def _draw_warning(self, layout):
        """Draw warning message."""
        row = layout.row()
        row.alignment = "CENTER"
        row.label(
            text=(
                "WARNING! THE FOLLOWING SETTINGS COULD MAKE BLENDLUXCORE "
                "UNUSABLE. "
            )
        )
        row = layout.row()
        row.alignment = "CENTER"
        row.label(
            text="*** DO NOT MODIFY UNLESS YOU KNOW WHAT YOU ARE DOING. ***"
        )
        layout.separator()
        layout.separator()

    def _draw_source_selection(self, layout):
        """Draw source selection subpanel."""
        header, layout = layout.panel("blendluxhelper.wheel_panel")

        header.label(text="Wheels")

        # If panel is closed, return
        if not layout:
            return

        # Source selector
        row = layout.row()
        split = row.split(factor=SPLIT_FACTOR, align=True)
        split.label(text="Wheel Source")
        row = split.row()
        row.prop(self, "wheel_source", expand=True)

        if self.wheel_source == "PyPI":
            row = layout.row()
            split = row.split(factor=SPLIT_FACTOR)
            split.label(text="Wheel Version (leave blank for default)")
            split.prop(self, "wheel_version", text="")
        elif self.wheel_source == "LocalWheel":
            # File
            row = layout.row()
            split = row.split(factor=SPLIT_FACTOR)
            split.label(text="Path to Wheel File")
            split.prop(self, "path_to_wheel", text="")

            row = layout.row()
            split = row.split(factor=SPLIT_FACTOR)
            split.label(text="Path to Additional Wheels Folder (optional)")
            split.prop(self, "path_to_wheel_deps", text="")

            row = layout.row()
            split = row.split(factor=SPLIT_FACTOR)
            split.label(text="Dependency Policy")
            split.prop(self, "no_deps")

            row = layout.row()
            split = row.split(factor=SPLIT_FACTOR)
            split.label(text="Index Policy")
            split.prop(self, "no_index")

        else:
            raise RuntimeError(f"Unhandled wheel source: {self.wheel_source}")

        row = layout.row()
        split = row.split(factor=SPLIT_FACTOR)
        split.label(text="Reloading Policy")
        split.prop(self, "reinstall_upon_reloading")

        # Settings file
        row = layout.row()
        split = row.split(factor=SPLIT_FACTOR)
        split.label(text="Output File")
        split.prop(self, "settings_file", text="", emboss=False)

        layout.separator()

        # Add 'reload scripts' operator button
        row = layout.row()
        split = row.split(factor=SPLIT_FACTOR)
        split.label(text="Scripts Reloading")
        split.operator(
            "blendluxhelper.reload_scripts",
            text="Reload Scripts",
            icon="FILE_REFRESH",
        )

    def _draw_editable_mode(self, layout):
        """Draw editable mode settings subpanel."""
        header, layout = layout.panel("blendluxhelper.editable_panel")

        header.label(text="Editable Mode")

        # If panel is closed, return
        if not layout:
            return

        # Add the symlink creation operator button
        row = layout.row()
        split = row.split(factor=SPLIT_FACTOR)
        split.label(text="Editable Installation")
        split.operator(
            "blendluxhelper.editable_install",
            text="Install Extension in Editable Mode",
            icon="GREASEPENCIL",
        )

    def draw(self, context):
        """Draw advanced settings panel (callback)."""
        layout = self.layout

        # Warn user about the potential settings impacts
        self._draw_warning(layout)

        # Draw source selection subpanel
        self._draw_source_selection(layout)
        layout.separator()

        # Draw editable mode subpanel
        self._draw_editable_mode(layout)


class BLH_OT_EditableInstall(bpy.types.Operator):
    """Install an extension (namely BlendLuxCore) in editable mode.

    This operator creates a symlink to an addon source directory in a given
    Blender repository, as documented here:

    https://developer.blender.org/docs/handbook/extensions/addon_dev_setup/\
#setting-up-project

    This allows to run and test the extension while continuing to develop it.

    Nota #1: To uninstall, simply use the standard procedure for uninstalling
    extensions.
    Nota #2: This feature is for development and debugging purposes only.
    In other case, please install extension according to standard procedure.
    """

    bl_idname = "blendluxhelper.editable_install"
    bl_label = "Install Editable"
    bl_options = {"REGISTER", "UNDO"}

    source_dir: bpy.props.StringProperty(
        name="Source Directory",
        description="Directory to link to",
        subtype="DIR_PATH",
    )
    blender_repo: bpy.props.StringProperty(
        name="Blender repository",
        description=(
            "Blender repository name where the link should be created. "
            "Nota: if this directory does not exist, it will be created."
        ),
        default="blc_dbg",
    )

    def execute(self, context):
        src = Path(self.source_dir).expanduser().resolve()
        dst_folder = Path(
            bpy.utils.user_resource(
                "EXTENSIONS", path=self.blender_repo, create=True
            )
        )
        symlink_name = src.parts[-1]
        symlink_name = symlink_name.lower()
        symlink_path = dst_folder / symlink_name

        # Validate source directory
        if not src.is_dir():
            self.report({"ERROR"}, f"Source directory does not exist: {src}")
            return {"CANCELLED"}

        # Ensure target folder exists
        try:
            dst_folder.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            self.report(
                {"ERROR"},
                f"Could not create target folder: {dst_folder}, error: {e}",
            )
            return {"CANCELLED"}

        if symlink_path.exists():
            self.report(
                {"ERROR"}, f"Symlink path already exists: {symlink_path}"
            )
            return {"CANCELLED"}

        try:
            if sys.platform == "win32":
                symlink_path.symlink_to(src, target_is_directory=True)
            else:
                symlink_path.symlink_to(src)
        except Exception as e:
            self.report({"ERROR"}, f"Failed to create symlink: {e}")
            return {"CANCELLED"}

        self.report({"INFO"}, f"Symlink created: {symlink_path} -> {src}")
        return {"FINISHED"}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)


class BLH_OT_ReloadScripts(bpy.types.Operator):
    """Reload all scripts."""

    bl_idname = "blendluxhelper.reload_scripts"
    bl_label = "Reload Scripts"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        # Attempt to reload the BlendLuxCore addon (must be installed)
        try:
            bpy.ops.script.reload(reload_scripts=True, extensions=True)
            self.report({"INFO"}, "Scripts reloaded.")
        except Exception as e:
            self.report({"ERROR"}, f"Failed to reload scripts: {e}")
            return {"CANCELLED"}
        return {"FINISHED"}


# Add to 3D View > Sidebar (N-panel) under a custom tab
class BLH_PT_Toolbar(bpy.types.Panel):
    bl_label = "BlendLuxHelper"
    bl_idname = "BLH_PT_toolbar"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "BlendLuxHelper"

    def draw(self, context):
        layout = self.layout
        layout.operator(
            "blendluxhelper.reload_scripts",
            text="Reload Scripts",
            icon="FILE_REFRESH",
        )


def register():
    bpy.utils.register_class(BLH_OT_EditableInstall)
    bpy.utils.register_class(BLH_OT_ReloadScripts)
    bpy.utils.register_class(BLH_PT_Toolbar)
    bpy.utils.register_class(BLHSettings)


def unregister():
    bpy.utils.unregister_class(BLH_OT_EditableInstall)
    bpy.utils.unregister_class(BLH_OT_ReloadScripts)
    bpy.utils.unregister_class(BLH_PT_Toolbar)
    bpy.utils.unregister_class(BLHSettings)
