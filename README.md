# TT-Ribs
A Blender based point cloud generator of mockups of Lyon fish-bones 

## Requirements
* Python
* Blender version > 4.0.2

## Exporting to ply
```bash
cd Src
blender --background ../Blender/Cave_V5_ready_toscript.blend --python export_to_ply.py
```

Open the resulting file (`bozo.ply`) e.g. with `https://point.love/`

## TODO
* Try the `apply_modifiers=True` exporting option.
* Try to assert Euler Characteristics before exportation