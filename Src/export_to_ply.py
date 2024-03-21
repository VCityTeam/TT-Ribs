import bpy
from bmesh_utils import bmesh_get_boundaries, bmesh_assert_genus_number_boundaries
from UI_utils import demote_UI_object_with_mesh_to_bmesh
import logging
import sys

prescribed_subdivision_level = 4

logger = logging.getLogger(__name__)
logging.basicConfig(filename="export_to_ply.log", encoding="utf-8", level=logging.DEBUG)

bpy.ops.wm.open_mainfile(filepath="../Blender/Cave_V5_ready_toscript.blend")

cave = bpy.data.objects["Cave"]

subdiv = cave.modifiers["Subdivision"]
subdiv.levels = prescribed_subdivision_level

bpy.ops.object.modifier_apply(modifier="Subdivision")
bpy.ops.object.modifier_apply(modifier="Displace.ground")
bpy.ops.object.modifier_apply(modifier="Displace.walls")
bpy.ops.object.modifier_apply(modifier="Displace_structure")

cave_bmesh = demote_UI_object_with_mesh_to_bmesh(cave)
bmesh_assert_genus_number_boundaries(
    cave_bmesh,
    5,  # Genus
    4,  # Number of boundaries
    "The topology of the cave is wrong.",
)
print("Boundaries: ", len(bmesh_get_boundaries(cave_bmesh)))

bpy.ops.object.bake(type="COMBINED")
bpy.ops.wm.ply_export(
    filepath="result_" + str(prescribed_subdivision_level) + ".ply",
    check_existing=True,
    forward_axis="Y",
    up_axis="Z",
    global_scale=1.0,
    apply_modifiers=False,
    export_selected_objects=True,
    export_uv=True,
    export_normals=True,
    export_colors="SRGB",
    export_triangulated_mesh=True,
    ascii_format=True,
    filter_glob="*.ply",
)
