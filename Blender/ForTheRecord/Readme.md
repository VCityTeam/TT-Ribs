# History of blender sources versions

## Cave

- `Cave_V5_ready_toscript.blend`: first version with every configuration
  already in set in order to minimise the actions that should be realized
  at the python/bpy run time.
- `Cave_V6.py`:
  - The texture images are now integrated, making the model an autonomous file
    (as opposed to V5 that required two files in the same directory).
  - A wall painting (a group of three hunters) is now integrated in the
    texture.
  - The stalactites extremities are now tagged within the
    "Change_size_stalactite" Vertex Group (allowing for a programmatic change
    of their height).
  - Some object names previously in french (e.g. "Array_est-ouest") now
    translated to english.
  - For some undocumented reason the genus is now 6 when V5 had genus 5.
  - Notes:
    - the renderer is erroneously set to be `Eevie` (that does not offer a
      `Bake` option)
    - the Tunnel object is not selected: exported PLY files are thus empty.
- `Cave_V6-1.py`: fixes of `Cave_V6.py` (as opposed to new features)
  - the renderer is set to be `Cycles`
  - the Tunnel object is now selected.

## Tunnel

- `Tunnel_V6.blend`: first complete version (part 1 and part2) of the tunnel
  system, including the (IRL non-existing) connection to the `Cave` at the
  lower bottom part of the system.
- `Tunnel_V6-1.blend`: the main tunnel is now selected (otherwise exportation
  to `ply` files is empty)
- `Tunnel_V7.blend`: V6 had four (topological) boundaries. Two of those
  boundaries are the expected tunnel openings (top level entry and bottom exit
  to the cave). Two of them are undesired/erroneous triangulation tears/cuts
  (due to an extensive manual modeling work in order to construct a single
  surface for the whole tunnel system). V7 removes those two undesired cuts
  thus restoring the expected two boundaries surface.
- `Tunnel_V7-1.blend`: "fixes" of V7
  - the maps/views used for the reconstruction of the tunnel system are now
    apparent (within Blender) even when the came axis is not strictly aligned
    with the world axis.
  - main tunnel system is now selected (otherwise exportation to `ply` files
    is empty).
