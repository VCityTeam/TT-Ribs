import bpy
from bpyhelpers import convert_ply_triangulation_to_point_cloud


def export_to_ply_files(triangulation_filename, verbose_mode):
    """Write (in `PLY` file format)
    - the triangulated surface
    - the associated point cloud

    Args:
        triangulation_filename (string): the named of the target PLY file to
        hold the triangulation
        verbose_mode (boolean): be verbose on CLI or not
    Note: the name of the point cloud file
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
    bpy.ops.wm.ply_export(
        filepath=triangulation_filename,
        check_existing=True,  # Check and warn on overwriting existing files
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
    convert_ply_triangulation_to_point_cloud(triangulation_filename, verbose_mode)
