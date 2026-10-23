bl_info = {
    "name": "Faia Blender Tools",
    "author": "Faia Studio",
    "version": (1, 0, 0),
    "blender": (4, 2, 0),
    "location": "Top Bar > FAIA",
    "description": "Production tools for game studios",
    "category": "Import-Export",
}

from . import props, export, check_destination, transform_checker, menu


def register():
    props.register()
    export.register()
    check_destination.register()
    transform_checker.register()
    menu.register()


def unregister():
    menu.unregister()
    transform_checker.unregister()
    check_destination.unregister()
    export.unregister()
    props.unregister()
