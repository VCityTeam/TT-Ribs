import bmesh
import bpyhelpers

def fill_holes(self, UI_geometry):
    """Fill in all holes (boundary edge list) with faces"""
    if not self.fill_holes:
        return
    # Getting UI based operators like bpy.ops.mesh.fill() or
    # bpy.ops.mesh.grid_fill() are difficult to get working since they
    # have implicit and most often under the hood "context" assumptions, 
    # that can only be found by tracking them in the sources (refer e.g. to 
    # this post
    # https://devtalk.blender.org/t/where-can-i-find-infromation-about-the-needed-environment-of-operators/20526/6 )
    # For example trying to get the following to work (it does run but
    # doesn't change the topology of the mesh) was a failure.
    #   bpy.ops.object.mode_set(mode='EDIT')
    #   my_obj = bpy.data.objects["Cave"]
    #   my_obj.select_set(True)
    #   bpy.context.view_layer.objects.active = my_obj
    #   bpy.ops.mesh.fill()
    # Hence, we resolve to using the "low" level interface.

    cave_bmesh = bpyhelpers.UI_demote_UI_object_with_mesh_to_bmesh(UI_geometry)
    boundaries = bpyhelpers.bmesh_get_boundaries(cave_bmesh)
    for boundary in boundaries:
        bmesh.ops.holes_fill(cave_bmesh, edges=boundary, sides=0)
    # Note: it is KEY to write the bmesh back to the mesh, refer to
    # https://docs.blender.org/api/current/bmesh.html#example-script
    cave_bmesh.to_mesh(UI_geometry.data)

