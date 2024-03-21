# The reference version of this file is probably encountered at
#  https://github.com/VCityTeam/TunNetGen/blob/master/WithModeller/bmesh_utils.py

import bpy
import bmesh


def promote_bmesh_to_UI_object(src_bmesh: bmesh.types.BMesh, name):
    # Not sure why the following transfer to a new mesh is really needed.
    # Maybe it is due to the latter arising of the bmesh module and the need
    # to keep it compatible with the UI way of things (?), refer to
    # https://blender.stackexchange.com/questions/134867/how-bpy-ops-mesh-differs-from-bmesh-ops
    mesh_result = bpy.data.meshes.new("Mesh")
    src_bmesh.to_mesh(mesh_result)
    src_bmesh.free()

    # Make it an object (which adds it to the scene (?))
    return bpy.data.objects.new(name, mesh_result)


def demote_UI_object_with_mesh_to_bmesh(src_object):
    bmesh_result = bmesh.new()
    bmesh_result.from_mesh(src_object.data)
    return bmesh_result


def UI_cleanup_default_scene():
    # Avoid showing the splash screen
    bpy.context.preferences.view.show_splash = False

    # Remove the defaul Cube from the original scene
    objs = bpy.data.objects
    objs.remove(objs["Cube"], do_unlink=True)
    objs.remove(objs["Camera"], do_unlink=True)
    objs.remove(objs["Light"], do_unlink=True)


def UI_boolean_union(
    base_object: bpy.types.Object, united_object: bpy.types.Object, delete=True
):
    """Realise the boolean union of the two bpy objects. Although the modifier
    is symmetric in terms of its operands, this function chooses (by default) to
    delete the second argument object.
    Args:
        base_object (_type_): the base object to which the united_object gets
                              united with.
        united_object (_type_): the object to be united from.
        delete (Boolean): when True united_object gets deleted
    """
    ### Boolean intersection
    # Although the debate/demand seems to date back to 2013, refer e.g. to
    #  https://blenderartists.org/t/bmesh-boolean/589555
    # bmesh module doesn't seem to offer boolean operators.
    # We thus resolve to working at the UI (bpy) level, refer e.g. to
    #   https://blender.stackexchange.com/questions/129853/boolean-on-two-simple-bmesh
    # and
    #   https://blender.stackexchange.com/questions/45004/how-to-make-boolean-modifiers-with-python
    # for its comment on applying the modifier.

    mod = base_object.modifiers.new(name="Boolean", type="BOOLEAN")
    mod.operation = "UNION"
    mod.object = united_object
    bpy.context.view_layer.objects.active = base_object
    bpy.ops.object.modifier_apply(modifier="Boolean")

    if delete:
        objs = bpy.data.objects
        objs.remove(united_object, do_unlink=True)
