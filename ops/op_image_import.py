import bpy
import os

from bpy.props import StringProperty, BoolProperty, EnumProperty


class SPIO_OT_import_image(bpy.types.Operator):
    """Import all image as reference (Empty object)"""

    bl_idname = 'spio.import_image'
    bl_label = 'Import Image'

    files: StringProperty()  # list of filepath, join with$$
    action: EnumProperty(items=[
        ('REF', 'Reference', ''),
        ('PLANE', 'PLANE', ''),
        ('NODES', 'NodeTree', ''),
    ])

    @classmethod
    def poll(_cls, context):
        if context.area.type == "VIEW_3D":
            return (
                    context.area.ui_type == "VIEW_3D"
                    and context.mode == "OBJECT")

        elif context.area.type == "NODE_EDITOR":
            return (
                    context.area.type == "NODE_EDITOR"
                    and context.area.ui_type in {'GeometryNodeTree', "ShaderNodeTree"}
                    and context.space_data.edit_tree is not None
            )

    def execute(self, context):
        if self.action == 'PLANE':
            from addon_utils import enable
            enable("io_import_images_as_planes")

        if self.action == 'NODES':
            location_X, location_Y = context.space_data.cursor_location

        for filepath in self.files.split('$$'):
            if self.action == 'PLANE':
                bpy.ops.import_image.to_plane(files=[{"name": filepath}])

            elif self.action == 'REF':
                bpy.ops.object.load_reference_image(filepath=filepath)

            elif self.action == 'NODES':
                bpy.ops.node.select_all(action='DESELECT')
                nt = context.space_data.edit_tree

                if context.area.ui_type == 'ShaderNodeTree':
                    node_type = 'ShaderNodeTexImage'
                elif context.area.ui_type == 'GeometryNodeTree':
                    node_type = 'GeometryNodeImageTexture'

                tex_node = nt.nodes.new(node_type)
                tex_node.location = location_X, location_Y
                # tex_node.hide = True
                location_Y -= 50
                location_X += 25

                tex_node.select = True
                nt.nodes.active = tex_node

                path = filepath
                image_name = os.path.basename(path)
                image = bpy.data.images.get(image_name) if image_name in bpy.data.images else bpy.data.images.load(
                    filepath=path)

                if node_type == 'ShaderNodeTexImage':
                    tex_node.image = image
                elif node_type == 'GeometryNodeImageTexture':
                    tex_node.inputs['Image'].default_value = image


        return {'FINISHED'}


def register():
    bpy.utils.register_class(SPIO_OT_import_image)


def unregister():
    bpy.utils.unregister_class(SPIO_OT_import_image)
