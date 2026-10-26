import bpy
import json
import math
import os
from collections import defaultdict


def _collect_scene(collection, parent_path=""):
    path = f"{parent_path}/{collection.name}" if parent_path else collection.name
    entries = []
    for obj in collection.objects:
        if obj.type in {'MESH', 'CURVE', 'ARMATURE'}:
            entries.append((obj, path))
    for child in collection.children:
        entries.extend(_collect_scene(child, path))
    return entries


def _to_ue_location(loc):
    return [round(loc.y * 100, 4), round(loc.x * 100, 4), round(loc.z * 100, 4)]


def _to_ue_rotation(euler):
    # Blender XYZ euler → Unreal (Pitch, Yaw, Roll)
    # Blender X=right, Y=fwd, Z=up → Unreal X=fwd, Y=right, Z=up
    pitch = round(math.degrees(euler.x), 4)
    yaw   = round(math.degrees(euler.z), 4)
    roll  = round(math.degrees(euler.y), 4)
    return [pitch, yaw, roll]


def _to_ue_scale(scale):
    return [round(scale.x, 4), round(scale.y, 4), round(scale.z, 4)]


class FAIA_OT_ExportSceneJSON(bpy.types.Operator):
    bl_idname = "faia.export_scene_json"
    bl_label = "Export Scene to JSON"
    bl_options = {'REGISTER'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=440)

    def draw(self, context):
        layout = self.layout
        s = context.scene.faia_settings
        col = layout.column(align=True)
        col.label(text="Scene Collection:")
        col.prop(s, "scene_collection", text="")
        col.separator()
        col.label(text="Assets Collection:")
        col.prop(s, "assets_collection", text="")
        col.separator()
        col.label(text="Output JSON:")
        col.prop(s, "json_export_path", text="")

    def execute(self, context):
        s = context.scene.faia_settings

        if s.scene_collection is None:
            self.report({'ERROR'}, "No scene collection selected.")
            return {'CANCELLED'}
        if s.assets_collection is None:
            self.report({'ERROR'}, "No assets collection selected.")
            return {'CANCELLED'}
        if not s.json_export_path:
            self.report({'ERROR'}, "No output path set.")
            return {'CANCELLED'}

        output_path = bpy.path.abspath(s.json_export_path)
        output_dir = os.path.dirname(output_path)
        if not os.path.isdir(output_dir):
            self.report({'ERROR'}, f"Output directory not found: '{output_dir}'")
            return {'CANCELLED'}

        # Build asset lookup: data pointer → asset name
        asset_map = {}
        for asset in s.assets_collection.objects:
            if asset.data:
                asset_map[asset.data.as_pointer()] = asset.name

        # Collect all scene objects with their folder path
        entries = _collect_scene(s.scene_collection)
        if not entries:
            self.report({'WARNING'}, "No compatible objects found in scene collection.")
            return {'CANCELLED'}

        # Validate — every object must be an instance of a known asset
        missing = [
            obj.name for obj, _ in entries
            if not obj.data or obj.data.as_pointer() not in asset_map
        ]
        if missing:
            self.report({'ERROR'}, f"Objects not in assets list: {', '.join(missing)}")
            return {'CANCELLED'}

        # Rename instances: group by asset, assign SM_AssetName_1, _2, ...
        groups = defaultdict(list)
        for obj, path in entries:
            asset_name = asset_map[obj.data.as_pointer()]
            groups[asset_name].append((obj, path))

        for asset_name, group in groups.items():
            for i, (obj, _) in enumerate(group, start=1):
                obj.name = f"{asset_name}_{i}"

        # Build JSON
        referenced_assets = set()
        objects_data = []

        for asset_name, group in groups.items():
            referenced_assets.add(asset_name)
            for obj, folder in group:
                loc, rot, scale = obj.matrix_world.decompose()
                euler = rot.to_euler('XYZ')
                objects_data.append({
                    "actor_name": obj.name,
                    "asset":      asset_name,
                    "folder":     folder,
                    "location":   _to_ue_location(loc),
                    "rotation":   _to_ue_rotation(euler),
                    "scale":      _to_ue_scale(scale),
                })

        payload = {
            "version": "1.0.0",
            "assets":  sorted(referenced_assets),
            "objects": objects_data,
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(payload, f, indent=2)

        self.report({'INFO'}, f"Scene exported: {len(objects_data)} object(s) → '{output_path}'")
        return {'FINISHED'}


def register():
    bpy.utils.register_class(FAIA_OT_ExportSceneJSON)


def unregister():
    bpy.utils.unregister_class(FAIA_OT_ExportSceneJSON)
