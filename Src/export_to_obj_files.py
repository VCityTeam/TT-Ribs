import bpy
from bpyhelpers import convert_obj_triangulation_to_point_cloud


def export_to_obj_files(obj_triangulation_filename, verbose_mode):
    """Write (in `OBJ` file format)
    - the triangulated surface
    - the associated point cloud

    Args:
        obj_triangulation_filename (string): the named of the target OBJ file
        to hold the triangulation
        verbose_mode (boolean): be verbose on CLI or not
    """
    # Debug note: when the UI is on (that is when is script is invocated with
    # "blender --python Cave.py") then the following ply_export() will
    # trigger the following runtime error:
    #    Operator bpy.ops.wm.ply_export.poll() failed, context is incorrect
    # Note that trying to use
    #    bpy.context.view_layer.objects.active = cave
    #    cave.select_set(True)
    # as suggested by
    #   https://blender.stackexchange.com/questions/275149/runtimeerror-operator-bpy-ops-object-convert-poll-failed-context-is-incorrec
    # won't help.
    # The source of this error is probably that objects should be selected ?!?!
    bpy.ops.wm.obj_export(
        filepath=obj_triangulation_filename,
        check_existing=True,  # Check and warn on overwriting existing files
        forward_axis="Y",
        up_axis="Z",
        global_scale=1.0,
        apply_modifiers=False,
        export_selected_objects=True,
        export_uv=False,
        export_normals=False,
        export_colors=True,
        export_triangulated_mesh=True,
        export_materials=False,  # Colors being at vertices, no materials needed
    )
    convert_obj_triangulation_to_point_cloud(obj_triangulation_filename, verbose_mode)
