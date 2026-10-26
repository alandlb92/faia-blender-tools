bl_info = {
    "name": "Faia Blender Tools",
    "author": "Faia Studio",
    "version": (1, 0, 8),
    "blender": (4, 2, 0),
    "location": "Top Bar > FAIA",
    "description": "Production tools for game studios",
    "category": "Import-Export",
}

from . import props, export, transform_checker, asset_checker, uv_world_scale, scene_exporter, menu


def register():
    props.register()
    export.register()
    transform_checker.register()
    asset_checker.register()
    uv_world_scale.register()
    scene_exporter.register()
    menu.register()


def unregister():
    menu.unregister()
    scene_exporter.unregister()
    uv_world_scale.unregister()
    asset_checker.unregister()
    transform_checker.unregister()
    export.unregister()
    props.unregister()
