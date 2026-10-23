import bpy


class FAIA_MT_UVMenu(bpy.types.Menu):
    bl_idname = "FAIA_MT_uv_menu"
    bl_label = "UV"

    def draw(self, context):
        self.layout.operator("faia.unwrap_size_based", icon='UV')


class FAIA_MT_MainMenu(bpy.types.Menu):
    bl_idname = "FAIA_MT_main_menu"
    bl_label = "FAIA"

    def draw(self, context):
        layout = self.layout
        layout.operator("faia.export_collection_fbx", icon='EXPORT')
        layout.separator()
        layout.operator("faia.transform_checker", icon='OBJECT_DATA')
        layout.separator()
        layout.menu("FAIA_MT_uv_menu", icon='UV_DATA')


def _draw_top_menu(self, context):
    self.layout.menu("FAIA_MT_main_menu")


def _draw_uv_map_menu(self, context):
    """Appended to the U shortcut menu in 3D Viewport Edit Mode."""
    self.layout.separator()
    self.layout.menu("FAIA_MT_uv_menu", icon='UV_DATA')


def _draw_uvs_menu(self, context):
    """Appended to the UV menu in the UV Editor."""
    self.layout.separator()
    self.layout.menu("FAIA_MT_uv_menu", icon='UV_DATA')


def register():
    bpy.utils.register_class(FAIA_MT_UVMenu)
    bpy.utils.register_class(FAIA_MT_MainMenu)
    bpy.types.TOPBAR_MT_editor_menus.append(_draw_top_menu)
    bpy.types.VIEW3D_MT_uv_map.append(_draw_uv_map_menu)
    bpy.types.IMAGE_MT_uvs.append(_draw_uvs_menu)


def unregister():
    bpy.types.IMAGE_MT_uvs.remove(_draw_uvs_menu)
    bpy.types.VIEW3D_MT_uv_map.remove(_draw_uv_map_menu)
    bpy.types.TOPBAR_MT_editor_menus.remove(_draw_top_menu)
    bpy.utils.unregister_class(FAIA_MT_MainMenu)
    bpy.utils.unregister_class(FAIA_MT_UVMenu)
