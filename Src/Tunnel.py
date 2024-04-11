import os
import logging
import bpy
import bpyhelpers
from argument_parser_helper import common_parser, parse_arguments


########### Globals
logger = logging.getLogger(__name__)
logging.basicConfig(filename="Tunnel.log", encoding="utf-8", level=logging.INFO)


class Tunnel:
    blender_pathfile = "../Blender/Tunnel_V6-1.blend"

    def __init__(self):
        self.parse_aguments()
        bpy.ops.wm.open_mainfile(filepath=Tunnel.blender_pathfile)
        self.tunnel = bpy.data.objects["Tunnel"]
        self.__apply_modifiers()
        self.__assert_resulting_topology()
        self.__export_to_ply_files()

    def parse_aguments(self):
        parser = common_parser()
        parser.add_argument(
            "--stalactite_factor",
            help="Vertical extension factor of the stalactites",
            default=1.0,
            type=float,
        )
        args = parse_arguments(parser)
        self.slactatite_strech_factor = args.stalactite_factor
        self.subdivision = args.subdivision
        self.outputdir = args.outputdir
        self.verbose = args.verbose

    def __apply_modifiers(self):
        """
        Parametrize the main modifiers and apply them
        """
        # The application of the modifiers is done through UI methods (prefixed
        # with "bpy.ops" as opposed to methods encountered in the bmesh module
        # that is prefixed with "bmesh."). Such methods apply on the objects
        # that are selected. Hence this temporary override of the context that
        # designates the active objects.
        with bpy.context.temp_override(
            selected_objects=[self.tunnel],
            object=self.tunnel,
            active_object=self.tunnel,
        ):

            subdiv = self.tunnel.modifiers["Subdivision"]
            subdiv.levels = self.subdivision
            bpy.ops.object.modifier_apply(modifier="Subdivision")
            bpy.ops.object.modifier_apply(modifier="Displace")
            ## FIXME: provide a parameter
            bpy.ops.object.modifier_apply(modifier="Decimate")

            # Note: baking _must_ occur after any modifier that acts on the vertices
            # of the mesh. If, for examples, baking were to be applied before
            # the "Subdivision" modifier, then the resulting vertices color would be
            # sub-sampled (because it would be aligned with the density of
            # vertices of the original mesh and not the final density resulting
            # from the application of the "Subdivision" modifier).
            bpy.ops.object.bake(type="COMBINED")

    def __assert_resulting_topology(self):
        #### Assert the topology of the resulting geometry
        tunnel_bmesh = bpyhelpers.UI_demote_UI_object_with_mesh_to_bmesh(self.tunnel)
        bpyhelpers.bmesh_assert_genus_number_boundaries(
            tunnel_bmesh,
            25,
            4,
            "The topology of the tunnel system is wrong.",
        )
        if self.verbose:
            bpyhelpers.bmesh_print_topological_characteristics(tunnel_bmesh)

    def __export_to_ply_files(self):
        ### Write the resulting files: start with the triangulation
        triangulation_filename = os.path.join(
            self.outputdir,
            "tunnel_sub_" + str(self.subdivision) + "_triangulation.ply",
        )
        # Debug note: when the UI is on (that is when is script is invocated with
        # "blender --python Tunnel.py") then the following ply_export() will
        # trigger the following runtime error:
        #    Operator bpy.ops.wm.ply_export.poll() failed, context is incorrect
        # Note that trying to use
        #    bpy.context.view_layer.objects.active = tunnel
        #    tunnel.select_set(True)
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
        bpyhelpers.convert_ply_triangulation_to_point_cloud(
            triangulation_filename, self.verbose
        )


if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    logging.basicConfig(
        filename="export_tunnel_to_ply.log", encoding="utf-8", level=logging.INFO
    )
    # The instantiation does it all
    tunnel = Tunnel()
