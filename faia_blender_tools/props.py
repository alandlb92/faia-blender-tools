import bpy


class FAIA_PG_Settings(bpy.types.PropertyGroup):
    # Export / Check Destination
    source_collection: bpy.props.PointerProperty(
        name="Collection",
        type=bpy.types.Collection,
    )
    destination_path: bpy.props.StringProperty(
        name="Destination",
        subtype='DIR_PATH',
    )
    include_children: bpy.props.BoolProperty(
        name="Include Child Collections",
        default=True,
    )

    # Scene JSON Exporter
    scene_collection: bpy.props.PointerProperty(
        name="Scene Collection",
        type=bpy.types.Collection,
    )
    assets_collection: bpy.props.PointerProperty(
        name="Assets Collection",
        type=bpy.types.Collection,
    )
    json_export_path: bpy.props.StringProperty(
        name="Output JSON",
        subtype='FILE_PATH',
    )

    # Transform Checker (independent from export settings)
    checker_collection: bpy.props.PointerProperty(
        name="Collection",
        type=bpy.types.Collection,
    )
    checker_include_children: bpy.props.BoolProperty(
        name="Include Children",
        default=True,
    )


def register():
    bpy.utils.register_class(FAIA_PG_Settings)
    bpy.types.Scene.faia_settings = bpy.props.PointerProperty(type=FAIA_PG_Settings)


def unregister():
    del bpy.types.Scene.faia_settings
    bpy.utils.unregister_class(FAIA_PG_Settings)
