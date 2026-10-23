import bpy
import math

from .utils import collect_objects, scale_is_clean, rotation_is_clean, get_vertex_count

# Stores transforms before any Apply so Revert can restore them.
_transform_backup: dict = {}


def _backup_obj(obj):
    return {
        'location': obj.location.copy(),
        'rotation_mode': obj.rotation_mode,
        'rotation_euler': obj.rotation_euler.copy(),
        'rotation_quaternion': obj.rotation_quaternion.copy(),
        'scale': obj.scale.copy(),
    }


def _apply_on_objects(context, objects, location, rotation, scale):
    """Apply transforms on a list of objects, returning selection to original state."""
    orig_active = context.view_layer.objects.active
    orig_selected = [o for o in context.selected_objects]

    for o in context.selected_objects:
        o.select_set(False)
    for obj in objects:
        obj.select_set(True)
    context.view_layer.objects.active = objects[0]

    try:
        bpy.ops.object.transform_apply(location=location, rotation=rotation, scale=scale)
    finally:
        for o in orig_selected:
            try:
                o.select_set(True)
            except ReferenceError:
                pass
        context.view_layer.objects.active = orig_active


# ── Per-object operators ───────────────────────────────────────────────────────

class FAIA_OT_ApplySingleScale(bpy.types.Operator):
    bl_idname = "faia.apply_single_scale"
    bl_label = "Apply Scale"
    bl_options = {'REGISTER', 'UNDO'}

    obj_name: bpy.props.StringProperty()

    def execute(self, context):
        obj = bpy.data.objects.get(self.obj_name)
        if obj is None:
            self.report({'ERROR'}, f"Object '{self.obj_name}' not found.")
            return {'CANCELLED'}
        _transform_backup[obj.name] = _backup_obj(obj)
        _apply_on_objects(context, [obj], location=False, rotation=False, scale=True)
        return {'FINISHED'}


class FAIA_OT_ApplySingleRotation(bpy.types.Operator):
    bl_idname = "faia.apply_single_rotation"
    bl_label = "Apply Rotation"
    bl_options = {'REGISTER', 'UNDO'}

    obj_name: bpy.props.StringProperty()

    def execute(self, context):
        obj = bpy.data.objects.get(self.obj_name)
        if obj is None:
            self.report({'ERROR'}, f"Object '{self.obj_name}' not found.")
            return {'CANCELLED'}
        _transform_backup[obj.name] = _backup_obj(obj)
        _apply_on_objects(context, [obj], location=False, rotation=True, scale=False)
        return {'FINISHED'}


# ── Apply All operators ────────────────────────────────────────────────────────

class FAIA_OT_ApplyAllScale(bpy.types.Operator):
    bl_idname = "faia.apply_all_scale"
    bl_label = "Apply Scale for All"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        s = context.scene.faia_settings
        if s.checker_collection is None:
            self.report({'ERROR'}, "No collection selected.")
            return {'CANCELLED'}

        objects = collect_objects(s.checker_collection, s.checker_include_children)
        dirty = [o for o in objects if not scale_is_clean(o)]

        if not dirty:
            self.report({'INFO'}, "All scales are already clean.")
            return {'FINISHED'}

        for obj in dirty:
            _transform_backup[obj.name] = _backup_obj(obj)

        _apply_on_objects(context, dirty, location=False, rotation=False, scale=True)
        self.report({'INFO'}, f"Applied scale to {len(dirty)} object(s). Use Revert to undo.")
        return {'FINISHED'}


class FAIA_OT_ApplyAllRotation(bpy.types.Operator):
    bl_idname = "faia.apply_all_rotation"
    bl_label = "Apply Rotation for All"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        s = context.scene.faia_settings
        if s.checker_collection is None:
            self.report({'ERROR'}, "No collection selected.")
            return {'CANCELLED'}

        objects = collect_objects(s.checker_collection, s.checker_include_children)
        dirty = [o for o in objects if not rotation_is_clean(o)]

        if not dirty:
            self.report({'INFO'}, "All rotations are already clean.")
            return {'FINISHED'}

        for obj in dirty:
            _transform_backup[obj.name] = _backup_obj(obj)

        _apply_on_objects(context, dirty, location=False, rotation=True, scale=False)
        self.report({'INFO'}, f"Applied rotation to {len(dirty)} object(s). Use Revert to undo.")
        return {'FINISHED'}


# ── Revert ────────────────────────────────────────────────────────────────────

class FAIA_OT_RevertTransforms(bpy.types.Operator):
    bl_idname = "faia.revert_transforms"
    bl_label = "Revert Last Apply"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        global _transform_backup
        if not _transform_backup:
            self.report({'WARNING'}, "No backup available.")
            return {'CANCELLED'}

        restored = 0
        for name, data in _transform_backup.items():
            obj = bpy.data.objects.get(name)
            if obj is None:
                print(f"[FAIA] Revert: '{name}' not found, skipping.")
                continue
            obj.location = data['location']
            obj.rotation_mode = data['rotation_mode']
            obj.rotation_euler = data['rotation_euler']
            obj.rotation_quaternion = data['rotation_quaternion']
            obj.scale = data['scale']
            restored += 1

        _transform_backup = {}
        self.report({'INFO'}, f"Reverted transforms on {restored} object(s).")
        return {'FINISHED'}


# ── Transform Checker popup ───────────────────────────────────────────────────

class FAIA_OT_TransformChecker(bpy.types.Operator):
    bl_idname = "faia.transform_checker"
    bl_label = "Transform Checker"
    bl_options = {'REGISTER'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=720)

    def draw(self, context):
        layout = self.layout
        s = context.scene.faia_settings

        # ── Collection selector ─────────────────────────────────────────────
        row = layout.row(align=True)
        row.prop(s, "checker_collection", text="Collection")
        row.prop(s, "checker_include_children", text="Children")

        layout.separator()

        # ── Global action buttons ───────────────────────────────────────────
        action_row = layout.row(align=True)
        action_row.operator("faia.apply_all_scale", icon='FULLSCREEN_ENTER')
        action_row.operator("faia.apply_all_rotation", icon='DRIVER_ROTATIONAL_DIFFERENCE')
        if _transform_backup:
            action_row.operator("faia.revert_transforms", icon='LOOP_BACK')

        layout.separator()

        if s.checker_collection is None:
            layout.label(text="Select a collection to inspect.", icon='INFO')
            return

        objects = collect_objects(s.checker_collection, s.checker_include_children)
        if not objects:
            layout.label(text="No compatible objects found.", icon='INFO')
            return

        # ── Table header ────────────────────────────────────────────────────
        header = layout.row()
        header.label(text="Object")
        header.label(text="Verts")
        header.label(text="Scale (X, Y, Z)")
        header.label(text="Rotation (X, Y, Z)")
        header.label(text="Apply")

        layout.separator(factor=0.3)

        # ── Table rows ──────────────────────────────────────────────────────
        for obj in sorted(objects, key=lambda o: o.name):
            sc_ok = scale_is_clean(obj)
            rot_ok = rotation_is_clean(obj)
            row_icon = 'CHECKMARK' if (sc_ok and rot_ok) else 'ERROR'

            row = layout.row(align=False)

            # Object name
            row.label(text=obj.name, icon=row_icon)

            # Vertex count
            vcount = get_vertex_count(obj)
            row.label(text=str(vcount) if vcount is not None else "–")

            # Scale
            s_val = obj.scale
            sc_col = row.row()
            sc_col.alert = not sc_ok
            sc_col.label(text=f"{s_val.x:.3f}  {s_val.y:.3f}  {s_val.z:.3f}")

            # Rotation (local euler, degrees)
            r = obj.rotation_euler
            rot_col = row.row()
            rot_col.alert = not rot_ok
            rot_col.label(
                text=(
                    f"{math.degrees(r.x):.1f}°  "
                    f"{math.degrees(r.y):.1f}°  "
                    f"{math.degrees(r.z):.1f}°"
                )
            )

            # Per-row apply buttons
            btn = row.row(align=True)
            op_s = btn.operator("faia.apply_single_scale", text="Scale")
            op_s.obj_name = obj.name
            op_r = btn.operator("faia.apply_single_rotation", text="Rot")
            op_r.obj_name = obj.name

    def execute(self, context):
        return {'FINISHED'}


# ── Registration ──────────────────────────────────────────────────────────────

_classes = [
    FAIA_OT_ApplySingleScale,
    FAIA_OT_ApplySingleRotation,
    FAIA_OT_ApplyAllScale,
    FAIA_OT_ApplyAllRotation,
    FAIA_OT_RevertTransforms,
    FAIA_OT_TransformChecker,
]


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
