import os
import collections
import logging
import bpy
import bmesh
import bpyhelpers
import mathutils
from argument_parser_helper import parse_arguments


########### Globals
logger = logging.getLogger(__name__)
logging.basicConfig(filename="export_to_ply.log", encoding="utf-8", level=logging.INFO)
IDENTIFICATION_THRESHOLD = 5.1  # Totally empirical and ad-hoc to this Cave


##########
def identifiable_boundary_indexes(boundaries):
    # Return (a list of) pairs of boundaries that are considered close enough to
    # be identifiable. Each boundary is first identified with the barycenter its
    # constituting verticies. Barycenters are then "compared".
    result = list()
    boundaries_barycenters = collections.deque(maxlen=len(boundaries))
    for boundary in boundaries:
        centroid = mathutils.Vector((0, 0, 0))
        for edge in boundary:
            centroid += edge.verts[0].co
        centroid /= len(boundary)
        boundaries_barycenters.append(centroid)
        # In case some visual debug of the centroid positions is required, use
        #    from debug_utils import create_sphere
        #    create_sphere("debug", mathutils.Matrix.Translation(centroid))
    for i in range(len(boundaries_barycenters)):
        for j in range(i + 1, len(boundaries_barycenters)):
            distance = (boundaries_barycenters[i] - boundaries_barycenters[j]).length
            if distance < IDENTIFICATION_THRESHOLD:
                result.append((i, j))
    return result


def replicate_to_build_grid(cave, grid_size_x, grid_size_y):
    logger.debug(
        "Number of boundaries prior to replications : "
        + str(
            len(
                bpyhelpers.bmesh_get_boundaries(
                    bpyhelpers.UI_demote_UI_object_with_mesh_to_bmesh(cave)
                )
            )
        ),
    )

    if grid_size_x > 1:
        copier_x = cave.modifiers["Array_est-ouest"]
        copier_x.count = grid_size_x
        # Note: in case debugging might requires a different offset
        # copier_x.constant_offset_displace = mathutils.Vector((75.0, -15.0, -8.0))
        bpy.ops.object.modifier_apply(modifier="Array_est-ouest")
    if grid_size_y > 1:
        copier_y = cave.modifiers["Array_nord-sud"]
        copier_y.count = grid_size_y
        bpy.ops.object.modifier_apply(modifier="Array_nord-sud")

    logger.debug(
        "Number of boundaries AFTER repetitions (but before bridging): "
        + str(
            len(
                bpyhelpers.bmesh_get_boundaries(
                    bpyhelpers.UI_demote_UI_object_with_mesh_to_bmesh(cave)
                )
            )
        ),
    )

    cave_bmesh = bpyhelpers.UI_demote_UI_object_with_mesh_to_bmesh(cave)
    boundaries = bpyhelpers.bmesh_get_boundaries(cave_bmesh)
    to_identify = identifiable_boundary_indexes(boundaries)
    logger.debug(
        "Number of boundary identifications to be realized " + str(len(to_identify))
    )
    logger.debug("Pair of boundaries to identify " + str(to_identify))
    for first_boundary_index, second_boundary_index in to_identify:
        first_edges = boundaries[first_boundary_index]
        second_edges = boundaries[second_boundary_index]
        bmesh.ops.bridge_loops(
            cave_bmesh,
            edges=first_edges + second_edges,
        )
    # Note: it is KEY to write the bmesh back to the mesh, refer to
    # https://docs.blender.org/api/current/bmesh.html#example-script
    cave_bmesh.to_mesh(cave.data)
    logger.debug(
        "Number of boundaries AFTER BRIDGING: "
        + str(
            len(
                bpyhelpers.bmesh_get_boundaries(
                    bpyhelpers.UI_demote_UI_object_with_mesh_to_bmesh(cave)
                )
            )
        )
    )


def main():
    args = parse_arguments()

    bpy.ops.wm.open_mainfile(filepath="../Blender/Cave_V5_ready_toscript.blend")

    cave = bpy.data.objects["Cave"]

    ##### Parametrize the modifiers and apply them
    # The application of the modifiers is done through UI methods (prefixed
    # with "bpy.ops" as opposed to methods encountered in the bmesh module
    # that is prefixed with "bmesh."). Such methods apply on the objects
    # that are selected. Hence this temporary override of the context that
    # designates the active objects.
    with bpy.context.temp_override(
        selected_objects=[cave], object=cave, active_object=cave
    ):

        subdiv = cave.modifiers["Subdivision"]
        subdiv.levels = args.subdivision
        bpy.ops.object.modifier_apply(modifier="Subdivision")
        bpy.ops.object.modifier_apply(modifier="Displace.ground")
        bpy.ops.object.modifier_apply(modifier="Displace.walls")
        bpy.ops.object.modifier_apply(modifier="Displace_structure")

        # Note: baking _must_ occur after any modifier that acts on the vertices
        # of the mesh. If, for examples, baking were to be applied before
        # the "Subdivision" modifier, then the resulting vertices color would be
        # sub-sampled (because it would be aligned with the density of
        # vertices of the original mesh and not the final density resulting
        # from the application of the "Subdivision" modifier).
        bpy.ops.object.bake(type="COMBINED")

        # When required proceed with the grid replication of the basic block
        if args.grid_size_x > 1 or args.grid_size_y > 1:
            replicate_to_build_grid(cave, args.grid_size_x, args.grid_size_y)

    #### Assert the topology of the resulting geometry
    resulting_bmesh = bpyhelpers.UI_demote_UI_object_with_mesh_to_bmesh(cave)
    # Concerning the expected genus:
    # the basic building block (the cave) genus is five. We build
    # a regular grid out of such an elementary building block:
    expected_genus = 5 * args.grid_size_x * args.grid_size_y
    # But when building a true grid (when there is replication in bother
    # directions) the gridification has a genus enhancing topological effect:
    expected_genus += (args.grid_size_x - 1) * (args.grid_size_y - 1)
    # Concerning the expected number of boundaries:
    # First let us notice that they are no boundaries internal to the
    # grid. Then let us notive that there is a boundary per elementary (cave)
    # block side sitting on the perimeter of the grid. Eventually, this is
    # equivalent to twice half of the perimeter:
    expected_boundary_number = 2 * (args.grid_size_x + args.grid_size_y)
    bpyhelpers.bmesh_assert_genus_number_boundaries(
        resulting_bmesh,
        expected_genus,
        expected_boundary_number,
        "The topology of the cave is wrong.",
    )
    if args.verbose:
        bpyhelpers.bmesh_print_topological_characteristics(resulting_bmesh)

    ### Write the resulting files: start with the triangulation
    triangulation_filename = os.path.join(
        args.outputdir,
        "cave_sub_"
        + str(args.subdivision)
        + "_grid_size_x_"
        + str(args.grid_size_x)
        + "_grid_size_y_"
        + str(args.grid_size_y)
        + "_triangulation.ply",
    )
    # Debug note: when the UI is on (that is when is script is invocated with
    # "blender --python export_to_ply.py") then the following ply_export() will
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
    bpyhelpers.convert_ply_triangulation_to_point_cloud(
        triangulation_filename, args.verbose
    )


if __name__ == "__main__":
    main()
