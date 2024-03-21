# TT-Ribs
A Blender based point cloud generator of mockups of Lyon fish-bones 

## Requirements
* Python
* Blender version > 4.0.2

## Exporting to ply

Using the blender binary
```bash
cd Src
blender --background ../Blender/Cave_V5_ready_toscript.blend --python export_to_ply.py
```

The python module way (avoids Blender UI installation) 
```bash
cd Src
python3.10 -m venv venv-3.10
source venv-3.10/bin/activate
pip3.10 install bpy
python export_to_ply.py
```

Open the resulting file (`result_*.ply`) e.g. with `https://point.love/`

## TODO
* Try the `apply_modifiers=True` exporting option.
