bl_info = {
    "name": "Faia Blender Tools",
    "author": "Faia Studio",
    "version": (1, 0, 4),
    "blender": (4, 2, 0),
    "location": "Top Bar > FAIA",
    "description": "Production tools for game studios",
    "category": "Import-Export",
}

from . import props, export, transform_checker, asset_checker, uv_world_scale, menu


def register():
    props.register()
    export.register()
    transform_checker.register()
    asset_checker.register()
    uv_world_scale.register()
    menu.register()


def unregister():
    menu.unregister()
    uv_world_scale.unregister()
    asset_checker.unregister()
    transform_checker.unregister()
    export.unregister()
    props.unregister()
