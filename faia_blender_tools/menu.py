import bpy


class FAIA_MT_MainMenu(bpy.types.Menu):
    bl_idname = "FAIA_MT_main_menu"
    bl_label = "FAIA"

    def draw(self, context):
        layout = self.layout
        layout.operator("faia.export_collection_fbx", icon='EXPORT')
        layout.operator("faia.check_destination_files", icon='VIEWZOOM')
        layout.separator()
        layout.operator("faia.transform_checker", icon='OBJECT_DATA')


def _draw_menu(self, context):
    self.layout.menu("FAIA_MT_main_menu")


def register():
    bpy.utils.register_class(FAIA_MT_MainMenu)
    bpy.types.TOPBAR_MT_editor_menus.append(_draw_menu)


def unregister():
    bpy.types.TOPBAR_MT_editor_menus.remove(_draw_menu)
    bpy.utils.unregister_class(FAIA_MT_MainMenu)
