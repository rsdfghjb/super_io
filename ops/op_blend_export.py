from __future__ import annotations

import bpy
import os
from os import getenv

import subprocess
import sys

from bpy.props import StringProperty, BoolProperty, EnumProperty
from .ops_super_import import import_icon

if sys.platform == "win32":
    from ..clipboard.windows import PowerShellClipboard as Clipboard
elif sys.platform == "darwin":
    from ..clipboard.darwin.mac import MacClipboard as Clipboard

from ..exporter.default_blend import post_process_blend_file

class ImageCopyDefault:
    @classmethod
    def poll(_cls, context):
        if sys.platform in {"darwin", "win32"}:
            return (
                    context.area.type == "VIEW_3D"
                    and context.active_object is not None
                    and context.active_object.mode == 'OBJECT'
                    and len(context.selected_objects) != 0
            )


class SPIO_OT_export_blend(ImageCopyDefault, bpy.types.Operator):
    """Export Selected objects to a blend file"""
    bl_idname = 'spio.export_blend'
    bl_label = 'Copy Blend'

    scripts_file_name:StringProperty(default = 'script_export_blend.py')

    def execute(self, context):
        bpy.ops.view3d.copybuffer()  # copy buffer

        ori_dir = context.preferences.filepaths.temporary_directory
        temp_dir = ori_dir
        if ori_dir == '':
            temp_dir = os.path.join(os.getenv('APPDATA'), os.path.pardir, 'Local', 'Temp')

        filepath = os.path.join(temp_dir, context.active_object.name + '.blend')
        if os.path.exists(filepath): os.remove(filepath)
        os.rename(os.path.join(temp_dir, 'copybuffer.blend'), filepath)

        post_process_blend_file(filepath,scripts_file_name=self.scripts_file_name)

        clipboard = Clipboard()
        clipboard.push_to_clipboard(paths=[filepath])

        self.report({'INFO'}, f'{context.active_object.name}.blend has been copied to Clipboard')

        return {'FINISHED'}



def register():
    bpy.utils.register_class(SPIO_OT_export_blend)


def unregister():
    bpy.utils.unregister_class(SPIO_OT_export_blend)
