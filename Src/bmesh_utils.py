# The reference version of this file is probably encountered at
#  https://github.com/VCityTeam/TunNetGen/blob/master/WithModeller/bmesh_utils.py

import sys
import logging
import bmesh
from collections import defaultdict

logger = logging.getLogger(__name__)


def bmesh_from_data(data):
    # We should be very suspicious about this dependency of bmesh
    # towards the UI (bpy module)
    import bpy

    """Create a bmesh out of data"""

    mesh = bpy.data.meshes.new("dummy_name_that_will_be_trashed")
    mesh.from_pydata(data["verts"], data["edges"], data["faces"])
    bmesh_result = bmesh.new()
    bmesh_result.from_mesh(mesh)
    del mesh

    return bmesh_result


def bmesh_duplicate(src_bmesh):
    # A bmesh is just a python object, refer e.g. to
    # https://blender.stackexchange.com/questions/90724/what-is-the-best-way-to-copy-append-geometry-from-one-bmesh-to-another
    return src_bmesh.copy()


def bmesh_get_boundary_edges(src_bmesh):
    return [ele for ele in src_bmesh.edges if ele.is_boundary]


def bmesh_triangulate_quad_faces(src_bmesh, faces):
    """Triangulate given faces

    Args:
        src_bmesh (_type_): the bmesh to which belong the faces
        faces (_type_): a list of faces to be triangulated
    """
    quad_faces = []
    for f in faces:
        if len(f.verts) == 4:
            quad_faces.append(f)
        else:
            print("bmesh_triangulate_quad_faces: non quad face given. Exiting")
            sys.exit(1)

    for q in quad_faces:
        bmesh.ops.connect_verts(
            src_bmesh,
            verts=[q.verts[0], q.verts[2]],
        )


def bmesh_join(list_of_bmeshes, normal_update=False):
    # This is copy of zeffi's answer found at
    # https://blender.stackexchange.com/questions/50160/scripting-low-level-join-meshes-elements-hopefully-with-bmesh/50186#50186
    """takes as input a list of bm references and outputs a single merged bmesh
    allows an additional 'normal_update=True' to force _normal_ calculations.
    """

    bm = bmesh.new()
    add_vert = bm.verts.new
    add_face = bm.faces.new
    add_edge = bm.edges.new

    for bm_to_add in list_of_bmeshes:
        offset = len(bm.verts)

        for v in bm_to_add.verts:
            add_vert(v.co)

        bm.verts.index_update()
        bm.verts.ensure_lookup_table()

        if bm_to_add.faces:
            for face in bm_to_add.faces:
                add_face(tuple(bm.verts[i.index + offset] for i in face.verts))
            bm.faces.index_update()

        if bm_to_add.edges:
            for edge in bm_to_add.edges:
                edge_seq = tuple(bm.verts[i.index + offset] for i in edge.verts)
                try:
                    add_edge(edge_seq)
                except ValueError:
                    # edge exists!
                    pass
            bm.edges.index_update()

    if normal_update:
        bm.normal_update()

    return bm


class Arc:
    """
    A ditch attempt to mimic halfedge data structure (refer e.g. to
    https://doc.cgal.org/latest/HalfedgeDS/index.html), or arcs i.e. oriented
    edges, on top of blender hidden edge structure in the _very resticted_ case
    of edge-walking on the boundary of a manifold.
    Because (alas) blender doesn't expose its walker functions to its
    python wrappers, refer e.g. to
      https://blender.community/c/rightclickselect/jTfbbc
      https://devtalk.blender.org/t/walking-edge-loops-across-a-mesh-from-c-to-python/14297
    edge walking is not that easy in bpy.
    This Arc edge class is a kludgy attempt to provide an edge boundary walker.
    """

    def __init__(self, v_src, edge):
        self.v_src = v_src
        if not edge.is_boundary:
            print("Arc::__init__: not a boundary edge constructor argument.")
            print("Exiting")
            sys.exit(1)
        self.edge = edge
        if self.edge.verts[0] == v_src:
            # Arc and edge are aligned accordingly
            self.v_dest = self.edge.verts[1]
        elif self.edge.verts[1] == v_src:
            self.v_dest = self.edge.verts[0]
        else:
            print("Arc::__init__: Arc and underlying edge got corrupted.")
            print("Exiting")
            sys.exit(1)

    def next_arc_on_boundary(self):
        # Take the destination vertex of the input boundary edge and return the next
        # edge (when there is only one) on that boundary, that is the boundary edge
        # having that destination vertex as source vertex.
        boundary_edges = [
            el for el in self.v_dest.link_edges if el.is_boundary and el != self.edge
        ]
        if len(boundary_edges) != 1:
            print("Arc::next_arc_on_boundary(): arc adjacent to no_face")
            print("Exiting")
            sys.exit(1)
        next_edge = boundary_edges[0]
        return Arc(self.v_dest, next_edge)

    def get_edge(self):
        return self.edge


def boundary_select(tags, entering_edge):
    logger.debug("Entering boundary select with edge " + str(entering_edge))
    tags[entering_edge] = True
    boundary_component_edges = [entering_edge]
    current_arc = Arc(entering_edge.verts[0], entering_edge)
    while True:
        next_arc = current_arc.next_arc_on_boundary()
        next_edge = next_arc.get_edge()
        if not tags[next_edge]:
            logger.debug(
                "Dealing with next_edge "
                + str(next_edge)
                + str(next_edge.verts[0])
                + str(next_edge.verts[1])
            )
            tags[next_edge] = True
            boundary_component_edges.append(next_edge)
            current_arc = next_arc
            continue
        # We circled back to the initial edge
        if next_edge != entering_edge:
            print("Where did we end up? Edges: ", next_edge, entering_edge)
            print("Exiting.")
            sys.exit(1)
        logger.debug("Exiting boundary select")
        break
    return boundary_component_edges


def bmesh_get_boundaries(src_bmesh):
    boundaries = []
    tags = defaultdict(bool)
    logger.debug("Entering bmesh_get_boundaries")
    while True:
        active_edges = [
            el for el in bmesh_get_boundary_edges(src_bmesh) if not tags[el]
        ]
        logger.debug("Number of active edges " + str(len(active_edges)))
        if not len(active_edges):
            logger.debug("Exiting bmesh_get_boundaries")
            return boundaries
        boundaries.append(boundary_select(tags, active_edges[0]))


def bmesh_get_number_of_boundaries(src_bmesh):
    return len(bmesh_get_boundaries(src_bmesh))


def bmesh_euler_characteristic(src_bmesh):
    # https://en.wikipedia.org/wiki/Euler_characteristic
    v_num = len(src_bmesh.verts)
    e_num = len(src_bmesh.edges)
    f_num = len(src_bmesh.faces)
    return v_num - e_num + f_num


def bmesh_assert_genus_number_boundaries(src_bmesh, genus, num_boundaries, msg):
    effective_num_boundaries = bmesh_get_number_of_boundaries(src_bmesh)
    if effective_num_boundaries != num_boundaries:
        print(msg)
        print("Erroneous number of boundaries: ")
        print(
            "   Was expecting ", num_boundaries, " but got ", effective_num_boundaries
        )
        print("Exiting.")
        sys.exit(1)
    effective_euler_characteristic = bmesh_euler_characteristic(src_bmesh)
    double_effective_genus = 2 - num_boundaries - effective_euler_characteristic
    if double_effective_genus != 2 * genus:
        print(msg)
        print("Erroneous genus: ")
        print("   Was expecting ", genus, " but got ", double_effective_genus / 2)
        print("Exiting.")
        sys.exit(1)
    # When the genus and the number of boundaries are correct then everything
    # should be fine. We nevertheless don't take _any_ risk
    expected_characteristic = 2 - 2 * genus - num_boundaries
    if effective_euler_characteristic != expected_characteristic:
        print(
            "Actual Euler characteristic is ",
            effective_euler_characteristic,
            " when it should be ",
            expected_characteristic,
            ".",
        )
        print("Exiting.")
        sys.exit(1)
    # All if fine and we have the expected topology
    return
