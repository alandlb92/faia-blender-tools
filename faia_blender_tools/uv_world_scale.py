import bpy
import bmesh
import math
from mathutils import Vector


def _poly_area_3d(world_verts):
    """Area of a convex/concave polygon in 3D using fan triangulation."""
    if len(world_verts) < 3:
        return 0.0
    total = Vector((0.0, 0.0, 0.0))
    for i in range(1, len(world_verts) - 1):
        a = world_verts[i] - world_verts[0]
        b = world_verts[i + 1] - world_verts[0]
        total += a.cross(b)
    return total.length * 0.5


def _poly_area_2d(uv_coords):
    """Signed area of a 2D polygon (shoelace formula)."""
    n = len(uv_coords)
    area = 0.0
    for i in range(n):
        j = (i + 1) % n
        area += uv_coords[i].x * uv_coords[j].y - uv_coords[j].x * uv_coords[i].y
    return abs(area) * 0.5


class FAIA_OT_UnwrapSizeBased(bpy.types.Operator):
    bl_idname = "faia.unwrap_size_based"
    bl_label = "Faia Unwrap Size Based"
    bl_description = "Unwrap and scale UVs so that 1 tile matches a real-world size in meters"
    bl_options = {'REGISTER', 'UNDO'}

    texture_size: bpy.props.FloatProperty(
        name="Texture World Size",
        description="Real-world size (meters) represented by one UV tile (0,0)→(1,1)",
        default=4.0,
        min=0.001,
        unit='LENGTH',
    )

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        self.layout.prop(self, "texture_size")

    def execute(self, context):
        obj = context.active_object

        if obj is None or obj.type != 'MESH' or context.mode != 'EDIT_MESH':
            self.report({'ERROR'}, "Active object must be a Mesh in Edit Mode.")
            return {'CANCELLED'}

        # Ensure at least one UV map exists
        if not obj.data.uv_layers:
            obj.data.uv_layers.new(name="UVMap")

        bm = bmesh.from_edit_mesh(obj.data)
        uv_layer = bm.loops.layers.uv.active

        if uv_layer is None:
            self.report({'ERROR'}, "No active UV map.")
            return {'CANCELLED'}

        # Select all and unwrap using existing seams
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.uv.unwrap(method='ANGLE_BASED', margin=0.001)

        # Refresh bmesh after unwrap
        bm = bmesh.from_edit_mesh(obj.data)
        uv_layer = bm.loops.layers.uv.active

        mat = obj.matrix_world
        total_3d_area = 0.0
        total_uv_area = 0.0

        for face in bm.faces:
            world_verts = [mat @ v.co for v in face.verts]
            total_3d_area += _poly_area_3d(world_verts)
            uv_coords = [loop[uv_layer].uv.copy() for loop in face.loops]
            total_uv_area += _poly_area_2d(uv_coords)

        if total_3d_area < 1e-10 or total_uv_area < 1e-10:
            self.report({'ERROR'}, "Could not compute UV or surface areas.")
            return {'CANCELLED'}

        # Scale UVs to match desired texel density
        current_density = math.sqrt(total_uv_area / total_3d_area)
        desired_density = 1.0 / self.texture_size
        k = desired_density / current_density

        for face in bm.faces:
            for loop in face.loops:
                loop[uv_layer].uv *= k

        # Anchor bottom-left corner to (0, 0)
        min_u = min(loop[uv_layer].uv.x for face in bm.faces for loop in face.loops)
        min_v = min(loop[uv_layer].uv.y for face in bm.faces for loop in face.loops)
        offset = Vector((-min_u, -min_v))

        for face in bm.faces:
            for loop in face.loops:
                loop[uv_layer].uv += offset

        bmesh.update_edit_mesh(obj.data)
        self.report({'INFO'}, f"UV unwrapped — 1 tile = {self.texture_size:.2f}m")
        return {'FINISHED'}


def register():
    bpy.utils.register_class(FAIA_OT_UnwrapSizeBased)


def unregister():
    bpy.utils.unregister_class(FAIA_OT_UnwrapSizeBased)
