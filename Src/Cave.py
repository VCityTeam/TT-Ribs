import os
import collections
import logging
import bpy
import bmesh
import bpyhelpers
import mathutils
from argument_parser_helper import common_parser, parse_arguments
from export_to_ply_files import export_to_ply_files
from export_to_obj_files import export_to_obj_files
from fill_holes import fill_holes


########### Globals
logger = logging.getLogger(__name__)
logging.basicConfig(filename="Cave.log", encoding="utf-8", level=logging.INFO)


class Cave:
    IDENTIFICATION_THRESHOLD = 5.1  # Totally empirical and ad-hoc to this Cave
    blender_pathfile = "../Blender/Cave_V6-1.blend"

    def __init__(self):
        self.parse_arguments()
        bpy.ops.wm.open_mainfile(filepath=Cave.blender_pathfile)
        self.cave = bpy.data.objects["Cave"]
        self.__apply_modifiers()
        self.__replicate_to_build_grid()
        self.__fill_holes()
        self.__assert_resulting_topology()
        self.__export_to_ply_files()
        self.__export_to_obj_files()

    def parse_arguments(self):
        parser = common_parser()
        parser.add_argument(
            "--grid_size_x",
            help="Size of the (sub)cave grid along the first axis",
            default=1,
            type=int,
        )
        parser.add_argument(
            "--grid_size_y",
            help="Size of the (sub)cave grid along the second axis",
            default=1,
            type=int,
        )
        parser.add_argument(
            "--stalactite_factor",
            help="Vertical extension factor of the stalactites",
            default=-25.0,
            type=float,
        )
        parser.add_argument(
            "--rugosity",
            help="Level of short range geometric noise (e.g. 0.2)",
            default=0.0,
            type=float,
        )
        parser.add_argument(
            "--relief",
            help="Level of mid range geometric noise (e.g. 0.7)",
            default=0.01,   # Defaulting to 0 disables the modifier
            type=float,
        )
        args = parse_arguments(parser)
        self.grid_size_x = args.grid_size_x
        self.grid_size_y = args.grid_size_y
        self.subdivision = args.subdivision
        self.fill_holes = args.fill_holes
        self.slactatite_stretch_factor = args.stalactite_factor
        self.rugosity = args.rugosity
        self.relief = args.relief
        self.outputdir = args.outputdir
        self.verbose = args.verbose
        self.no_ply_export = args.no_ply_export
        self.no_obj_export = args.no_obj_export

    def __apply_modifiers(self):
        """
        Parametrize the modifiers (of the basic cave block that is without the
        grid modifiers), apply them and "bake" the vertex colors
        """
        # The application of the modifiers is done through UI methods (prefixed
        # with "bpy.ops" as opposed to methods encountered in the bmesh module
        # that is prefixed with "bmesh."). Such methods apply on the objects
        # that are selected. Hence this temporary override of the context that
        # designates the active objects.
        with bpy.context.temp_override(
            selected_objects=[self.cave], object=self.cave, active_object=self.cave
        ):

            stalactites = self.cave.modifiers["SimpleDeform"]
            stalactites.factor = self.slactatite_stretch_factor
            bpy.ops.object.modifier_apply(modifier="SimpleDeform")

            subdiv = self.cave.modifiers["Subdivision"]
            subdiv.levels = self.subdivision
            bpy.ops.object.modifier_apply(modifier="Subdivision")

            bpy.ops.object.modifier_apply(modifier="Displace.ground")

            relief_geometric_noise = self.cave.modifiers["Displace.walls"]
            relief_geometric_noise.strength = self.relief
            bpy.ops.object.modifier_apply(modifier="Displace.walls")

            rugosity_geometric_noise = self.cave.modifiers["Displace_structure"]
            rugosity_geometric_noise.strength = self.rugosity
            bpy.ops.object.modifier_apply(modifier="Displace_structure")

            # Note: baking _must_ occur after any modifier that acts on the vertices
            # of the mesh. If, for examples, baking were to be applied before
            # the "Subdivision" modifier, then the resulting vertices color would be
            # sub-sampled (because it would be aligned with the density of
            # vertices of the original mesh and not the final density resulting
            # from the application of the "Subdivision" modifier).
            bpy.ops.object.bake(type="COMBINED")

    def __identifiable_boundary_indexes(self, boundaries):
        # Return (a list of) pairs of boundaries that are considered close enough to
        # be identifiable. Each boundary is first identified with the barycenter its
        # constituting vertices. Barycenters are then "compared".
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
                distance = (
                    boundaries_barycenters[i] - boundaries_barycenters[j]
                ).length
                if distance < Cave.IDENTIFICATION_THRESHOLD:
                    result.append((i, j))
        return result

    def __fill_holes(self):
        """Fill in all holes (boundary edge list) with faces"""
        if not self.fill_holes:
            return
        fill_holes(self.cave)

    def __replicate_to_build_grid(self):
        if self.grid_size_x <= 1 and self.grid_size_y <= 1:
            return
        logger.debug(
            "Number of boundaries prior to replications : "
            + str(
                len(
                    bpyhelpers.bmesh_get_boundaries(
                        bpyhelpers.UI_demote_UI_object_with_mesh_to_bmesh(self.cave)
                    )
                )
            ),
        )

        # The application of the modifiers is done through UI methods (prefixed
        # with "bpy.ops" as opposed to methods encountered in the bmesh module
        # that is prefixed with "bmesh."). Such methods apply on the objects
        # that are selected. Hence this temporary override of the context that
        # designates the active objects.
        with bpy.context.temp_override(
            selected_objects=[self.cave], object=self.cave, active_object=self.cave
        ):
            if self.grid_size_x > 1:
                copier_x = self.cave.modifiers["Array_Y"]
                copier_x.count = self.grid_size_x
                # Note: in case debugging might requires a different offset
                # copier_x.constant_offset_displace = mathutils.Vector((75.0, -15.0, -8.0))
                bpy.ops.object.modifier_apply(modifier="Array_Y")
            if self.grid_size_y > 1:
                copier_y = self.cave.modifiers["Array_X"]
                copier_y.count = self.grid_size_y
                bpy.ops.object.modifier_apply(modifier="Array_X")

            logger.debug(
                "Number of boundaries AFTER repetitions (but before bridging): "
                + str(
                    len(
                        bpyhelpers.bmesh_get_boundaries(
                            bpyhelpers.UI_demote_UI_object_with_mesh_to_bmesh(self.cave)
                        )
                    )
                ),
            )

            cave_bmesh = bpyhelpers.UI_demote_UI_object_with_mesh_to_bmesh(self.cave)
            boundaries = bpyhelpers.bmesh_get_boundaries(cave_bmesh)
            to_identify = self.__identifiable_boundary_indexes(boundaries)
            logger.debug(
                "Number of boundary identifications to be realized "
                + str(len(to_identify))
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
            cave_bmesh.to_mesh(self.cave.data)
            logger.debug(
                "Number of boundaries AFTER BRIDGING: "
                + str(
                    len(
                        bpyhelpers.bmesh_get_boundaries(
                            bpyhelpers.UI_demote_UI_object_with_mesh_to_bmesh(self.cave)
                        )
                    )
                )
            )

    def __assert_resulting_topology(self):
        """
        Assert the topology of the resulting geometry
        """
        resulting_bmesh = bpyhelpers.UI_demote_UI_object_with_mesh_to_bmesh(self.cave)
        # Concerning the expected genus:
        # the basic building block (the cave) genus is six. We build
        # a regular grid out of such an elementary building block:
        expected_genus = 6 * self.grid_size_x * self.grid_size_y
        # But when building a true grid (when there is replication in bother
        # directions) the gridification has a genus enhancing topological effect:
        expected_genus += (self.grid_size_x - 1) * (self.grid_size_y - 1)
        if self.fill_holes:
            expected_boundary_number = 0
        else:
            # Concerning the expected number of boundaries:
            # First let us notice that they are no boundaries internal to the
            # grid. Then let us notice that there is a boundary per elementary (cave)
            # block side sitting on the perimeter of the grid. Eventually, this is
            # equivalent to twice half of the perimeter:
            expected_boundary_number = 2 * (self.grid_size_x + self.grid_size_y)
        bpyhelpers.bmesh_assert_genus_number_boundaries(
            resulting_bmesh,
            expected_genus,
            expected_boundary_number,
            "The topology of the cave is wrong.",
        )
        if self.verbose:
            bpyhelpers.bmesh_print_topological_characteristics(resulting_bmesh)

    def __export_triangulation_basename(self):
        filename = (
            "cave_sub_"
            + str(self.subdivision)
            + "_grid_size_x_"
            + str(self.grid_size_x)
            + "_grid_size_y_"
            + str(self.grid_size_y)
        )
        if self.fill_holes:
            filename += "_no_boundaries"
        filename += "_triangulation"
        return os.path.join(self.outputdir, filename)

    def __export_to_ply_files(self):
        """Write the resulting PLY files"""
        ply_triangulation_filename = self.__export_triangulation_basename() + ".ply"
        print(ply_triangulation_filename)
        export_to_ply_files(ply_triangulation_filename, self.verbose)

    def __export_to_obj_files(self):
        """Write the resulting OBJ files"""
        if self.no_obj_export:
            return
        obj_triangulation_filename = self.__export_triangulation_basename() + ".obj"
        export_to_obj_files(obj_triangulation_filename, self.verbose)


if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    logging.basicConfig(
        filename="export_cave_to_ply.log", encoding="utf-8", level=logging.INFO
    )
    cave = Cave()
