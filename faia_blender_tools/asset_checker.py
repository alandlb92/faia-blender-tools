import bpy

from .utils import FAIA_SUPPORTED_TYPES


def _check_scene_assets(context):
    objects = [o for o in context.scene.objects if o.type in FAIA_SUPPORTED_TYPES]

    asset_data_map = {}
    assets = []

    for obj in objects:
        if obj.asset_data is not None:
            assets.append(obj)
            if obj.data:
                asset_data_map[obj.data] = obj

    linked_copies = []
    unexpected = []

    for obj in objects:
        if obj.asset_data is not None:
            continue
        if obj.data and obj.data in asset_data_map:
            linked_copies.append((obj, asset_data_map[obj.data]))
        else:
            unexpected.append(obj)

    return (
        sorted(assets, key=lambda o: o.name),
        sorted(linked_copies, key=lambda t: t[0].name),
        sorted(unexpected, key=lambda o: o.name),
    )


class FAIA_OT_SelectObject(bpy.types.Operator):
    bl_idname = "faia.select_object"
    bl_label = "Select"
    bl_options = {'REGISTER', 'UNDO'}

    obj_name: bpy.props.StringProperty()

    def execute(self, context):
        obj = bpy.data.objects.get(self.obj_name)
        if obj is None:
            self.report({'ERROR'}, f"Object '{self.obj_name}' not found.")
            return {'CANCELLED'}
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        context.view_layer.objects.active = obj
        return {'FINISHED'}


class FAIA_OT_AssetChecker(bpy.types.Operator):
    bl_idname = "faia.asset_checker"
    bl_label = "Asset Checker"
    bl_options = {'REGISTER'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=460)

    def draw(self, context):
        layout = self.layout
        assets, linked_copies, unexpected = _check_scene_assets(context)

        if not assets:
            layout.label(text="No marked assets found in scene.", icon='INFO')
            return

        # ── Summary ───────────────────────────────────────────────────────
        row = layout.row(align=True)
        row.label(text=f"Assets: {len(assets)}", icon='SCENE_DATA')
        row.label(text=f"Linked: {len(linked_copies)}", icon='LINKED')
        if unexpected:
            row.alert = True
            row.label(text=f"Unexpected: {len(unexpected)}", icon='ERROR')
        else:
            row.label(text="Unexpected: 0", icon='CHECKMARK')
        layout.separator()

        # ── Assets ────────────────────────────────────────────────────────
        box = layout.box()
        box.label(text=f"Assets ({len(assets)}):", icon='SCENE_DATA')
        for obj in assets:
            row = box.row()
            row.label(text=obj.name, icon='OBJECT_DATA')
            op = row.operator("faia.select_object", text="Select", icon='RESTRICT_SELECT_OFF')
            op.obj_name = obj.name

        # ── Linked Copies ─────────────────────────────────────────────────
        if linked_copies:
            box = layout.box()
            box.label(text=f"Linked Copies ({len(linked_copies)}):", icon='LINKED')
            for obj, source in linked_copies:
                row = box.row()
                row.label(text=f"{obj.name}  →  {source.name}", icon='FILE_REFRESH')
                op = row.operator("faia.select_object", text="Select", icon='RESTRICT_SELECT_OFF')
                op.obj_name = obj.name

        # ── Unexpected ────────────────────────────────────────────────────
        if unexpected:
            box = layout.box()
            box.label(text=f"Unexpected ({len(unexpected)}):", icon='ERROR')
            for obj in unexpected:
                row = box.row()
                row.label(text=obj.name, icon='ORPHAN_DATA')
                op = row.operator("faia.select_object", text="Select", icon='RESTRICT_SELECT_OFF')
                op.obj_name = obj.name
        else:
            layout.label(text="Scene looks clean.", icon='CHECKMARK')

    def execute(self, context):
        return {'FINISHED'}


_classes = [
    FAIA_OT_SelectObject,
    FAIA_OT_AssetChecker,
]


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
