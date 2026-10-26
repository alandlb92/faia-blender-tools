import bpy
import re

FAIA_SUPPORTED_TYPES = {'MESH', 'CURVE', 'ARMATURE'}
TRANSFORM_TOLERANCE = 1e-4


def collect_objects(collection, include_children):
    """Return a deduplicated list of FBX-compatible objects from a collection."""
    objects = set()
    for obj in collection.objects:
        if obj.type in FAIA_SUPPORTED_TYPES:
            objects.add(obj)
        else:
            print(f"[FAIA] Skipping '{obj.name}' (type: {obj.type})")
    if include_children:
        for child in collection.children:
            objects.update(collect_objects(child, include_children))
    return list(objects)


def scale_is_clean(obj):
    return all(abs(v - 1.0) < TRANSFORM_TOLERANCE for v in obj.scale)


def rotation_is_clean(obj):
    return all(abs(v) < TRANSFORM_TOLERANCE for v in obj.rotation_euler)


def get_vertex_count(obj):
    if obj.type == 'MESH' and obj.data:
        return len(obj.data.vertices)
    return None


def sanitize_filename(name):
    return re.sub(r'[\\/*?:"<>|]', '_', name)


def get_fbx_export_kwargs(filepath):
    return dict(
        filepath=filepath,
        use_selection=True,
        object_types={'MESH', 'ARMATURE', 'OTHER'},
        add_leaf_bones=False,
        embed_textures=False,
        bake_anim=False,
        global_scale=1.0,
        apply_unit_scale=True,
        apply_scale_options='FBX_SCALE_NONE',
        use_space_transform=True,
        axis_forward='-Z',
        axis_up='Y',
        path_mode='AUTO',
    )


def get_data_collection(obj_type):
    return {
        'MESH': bpy.data.meshes,
        'CURVE': bpy.data.curves,
        'ARMATURE': bpy.data.armatures,
    }.get(obj_type)
