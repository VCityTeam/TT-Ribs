import bpy

cave = bpy.data.objects["Cave"]
cave.select_set(True)

# bpy.context.space_data.context = "MODIFIER"
bpy.ops.object.modifier_apply(modifier="Subdivision")
bpy.ops.object.modifier_apply(modifier="Displace.ground")
bpy.ops.object.modifier_apply(modifier="Displace.walls")
bpy.ops.object.modifier_apply(modifier="Displace_structure")

# bpy.context.space_data.context = "RENDER"
bpy.ops.object.bake(type="COMBINED")
bpy.ops.wm.ply_export(
    filepath="bozo.ply",
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
