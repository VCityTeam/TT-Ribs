import os
import logging
import bpy
import bpyhelpers
from argument_parser_helper import common_parser, parse_arguments
from export_to_ply_files import export_to_ply_files
from export_to_obj_files import export_to_obj_files
from fill_holes import fill_holes

class Tunnel:
    blender_pathfile = "../Blender/Tunnel_V7-1.blend"

    def __init__(self):
        self.parse_aguments()
        bpy.ops.wm.open_mainfile(filepath=Tunnel.blender_pathfile)
        self.tunnel = bpy.data.objects["Tunnel"]
        self.__apply_modifiers()
        self.__fill_holes()
        self.__assert_resulting_topology()
        self.__export_to_ply_files()
        self.__export_to_obj_files()

    def parse_aguments(self):
        parser = common_parser()
        parser.add_argument(
            "--relief",
            help="Level of mid range geometric noise (e.g. 1.0)",
            default=0.01,  # Defaulting to 0 (quietly) disables the modifier
            type=float,
        )
        args = parse_arguments(parser)
        self.subdivision = args.subdivision
        self.relief = args.relief
        self.fill_holes = args.fill_holes
        self.outputdir = args.outputdir
        self.verbose = args.verbose
        self.no_ply_export = args.no_ply_export
        self.no_obj_export = args.no_obj_export

    def __apply_modifiers(self):
        """
        Parametrize the modifiers, apply them and "bake" the vertex colors.
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
            relief_geometric_noise = self.tunnel.modifiers["Displace"]
            relief_geometric_noise.strength = self.relief
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

    def __fill_holes(self):
        """Fill in all holes (boundary edge list) with faces"""
        if not self.fill_holes:
            return
        fill_holes(self.tunnel)

    def __assert_resulting_topology(self):
        """
        Assert the topology of the resulting geometry
        """
        if self.fill_holes:
            expected_boundary_number = 0
        else:
            expected_boundary_number = 2

        tunnel_bmesh = bpyhelpers.UI_demote_UI_object_with_mesh_to_bmesh(self.tunnel)
        bpyhelpers.bmesh_assert_genus_number_boundaries(
            tunnel_bmesh,
            25,
            expected_boundary_number,
            "The topology of the tunnel system is wrong.",
        )
        if self.verbose:
            bpyhelpers.bmesh_print_topological_characteristics(tunnel_bmesh)

    def __export_triangulation_basename(self):
        filename = "tunnel_sub_" + str(self.subdivision)
        if self.fill_holes:
            filename += "_no_boundaries"
        filename += "_triangulation"
        filename += "_relief_" + str(self.relief)
        return os.path.join(self.outputdir, filename)

    def __export_to_ply_files(self):
        """Write the resulting PLY files"""
        if self.no_ply_export:
            return
        ply_triangulation_filename = self.__export_triangulation_basename() + ".ply"
        export_to_ply_files(ply_triangulation_filename, self.verbose)

    def __export_to_obj_files(self):
        """Write the resulting OBJ files"""
        if self.no_obj_export:
            return
        obj_triangulation_filename = self.__export_triangulation_basename() + ".obj"
        export_to_obj_files(obj_triangulation_filename, self.verbose)


if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    logging.basicConfig(filename="tunnel.log", encoding="utf-8", level=logging.INFO)
    # The instantiation does it all
    tunnel = Tunnel()
