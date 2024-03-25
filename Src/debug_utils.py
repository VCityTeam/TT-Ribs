import bpy
import bmesh
import mathutils


def create_sphere(name, matrix):
    # Create an empty mesh and the object.
    mesh = bpy.data.meshes.new(name)
    basic_sphere = bpy.data.objects.new(name, mesh)

    # Add the object into the scene.
    bpy.context.collection.objects.link(basic_sphere)

    # Construct the bmesh sphere and assign it to the blender mesh.
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=16, v_segments=16, radius=1, matrix=matrix)
    bm.to_mesh(mesh)
    bm.free()


if __name__ == "__main__":
    create_sphere("dummy_name", matrix=mathutils.Matrix.Translation((5.0, 0.0, 0.0)))
