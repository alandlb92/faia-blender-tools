import bpy
import os
import traceback

from .utils import (
    collect_objects,
    get_fbx_export_kwargs,
    sanitize_filename,
    get_data_collection,
)


class FAIA_OT_ExportCollectionFBX(bpy.types.Operator):
    bl_idname = "faia.export_collection_fbx"
    bl_label = "Export Collection to FBX"
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
            self.report({'ERROR'}, f"Invalid destination path: '{dest}'")
            return {'CANCELLED'}

        objects = collect_objects(s.source_collection, s.include_children)
        if not objects:
            self.report({'WARNING'}, "No compatible objects found in collection.")
            return {'CANCELLED'}

        if context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')

        original_active = context.view_layer.objects.active
        original_selected = [o for o in context.selected_objects]

        for o in context.selected_objects:
            o.select_set(False)

        exported = 0
        failed = 0

        try:
            for obj in objects:
                if self._export_single(context, obj, dest):
                    exported += 1
                else:
                    failed += 1
        finally:
            for o in original_selected:
                try:
                    o.select_set(True)
                except ReferenceError:
                    pass
            context.view_layer.objects.active = original_active

        if failed == 0:
            self.report({'INFO'}, f"Exported {exported} object(s) to '{dest}'.")
        else:
            self.report(
                {'WARNING'},
                f"Exported {exported} object(s). {failed} failed — check console.",
            )
        return {'FINISHED'}

    def _export_single(self, context, obj, dest_dir):
        copy = None
        copy_data = None
        try:
            copy_data = obj.data.copy() if obj.data else None
            copy = obj.copy()
            if copy_data:
                copy.data = copy_data
            copy.name = f"__faia_temp_{obj.name}__"

            context.scene.collection.objects.link(copy)
            copy.hide_viewport = False
            copy.hide_render = False

            # Snapshot world transform before any operation
            world_matrix = obj.matrix_world.copy()

            copy.parent = None
            context.view_layer.update()
            copy.matrix_world = world_matrix
            copy.location = (0.0, 0.0, 0.0)

            for o in context.selected_objects:
                o.select_set(False)
            copy.select_set(True)
            context.view_layer.objects.active = copy

            safe_name = sanitize_filename(obj.name)
            filepath = os.path.join(dest_dir, f"{safe_name}.fbx")
            bpy.ops.export_scene.fbx(**get_fbx_export_kwargs(filepath))
            return True

        except Exception as e:
            print(f"[FAIA] ERROR exporting '{obj.name}': {e}")
            traceback.print_exc()
            return False

        finally:
            if copy is not None:
                try:
                    bpy.data.objects.remove(copy, do_unlink=True)
                except Exception:
                    pass
            if copy_data is not None:
                dc = get_data_collection(obj.type)
                try:
                    if dc and copy_data.name in dc:
                        dc.remove(copy_data)
                except Exception:
                    pass


def register():
    bpy.utils.register_class(FAIA_OT_ExportCollectionFBX)


def unregister():
    bpy.utils.unregister_class(FAIA_OT_ExportCollectionFBX)
