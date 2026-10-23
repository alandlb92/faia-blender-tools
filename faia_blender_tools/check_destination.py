import bpy
import os

from .utils import collect_objects


class FAIA_OT_CheckDestinationFiles(bpy.types.Operator):
    bl_idname = "faia.check_destination_files"
    bl_label = "Check Destination Files"
    bl_options = {'REGISTER'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=420)

    def draw(self, context):
        layout = self.layout
        s = context.scene.faia_settings
        col = layout.column(align=True)
        col.label(text="Collection:")
        col.prop(s, "source_collection", text="")
        col.separator()
        col.label(text="Destination Folder:")
        col.prop(s, "destination_path", text="")
        col.separator()
        col.prop(s, "include_children")

    def execute(self, context):
        s = context.scene.faia_settings

        if s.source_collection is None:
            self.report({'ERROR'}, "No collection selected.")
            return {'CANCELLED'}

        dest = bpy.path.abspath(s.destination_path)
        if not dest or not os.path.isdir(dest):
            self.report({'ERROR'}, f"Destination path does not exist: '{dest}'")
            return {'CANCELLED'}

        objects = collect_objects(s.source_collection, s.include_children)
        if not objects:
            self.report({'WARNING'}, "No compatible objects found in collection.")
            return {'CANCELLED'}

        try:
            existing = {
                f.lower()
                for f in os.listdir(dest)
                if f.lower().endswith('.fbx')
            }
        except PermissionError as e:
            self.report({'ERROR'}, f"Cannot read destination folder: {e}")
            return {'CANCELLED'}

        present = [o.name for o in objects if f"{o.name}.fbx".lower() in existing]
        missing = [o.name for o in objects if f"{o.name}.fbx".lower() not in existing]

        if not missing:
            self.report({'INFO'}, "All objects already exist in destination.")
        else:
            exist_str = ", ".join(present) if present else "none"
            miss_str = ", ".join(missing)
            self.report({'WARNING'}, f"Exist: [{exist_str}] | Missing: [{miss_str}]")

        return {'FINISHED'}


def register():
    bpy.utils.register_class(FAIA_OT_CheckDestinationFiles)


def unregister():
    bpy.utils.unregister_class(FAIA_OT_CheckDestinationFiles)
