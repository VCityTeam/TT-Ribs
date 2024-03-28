# Ribs

**Table of content**
<!-- TOC -->

- [Requirements](#requirements)
- [Installation](#installation)
- [Exporting to ply](#exporting-to-ply)
- [TODO](#todo)
- [The Cave](#the-cave)
  - [Different rendering tools](#different-rendering-tools)
  - [Triangulation vs point cloud](#triangulation-vs-point-cloud)
  - [The effect of the subdivision level on the geometry](#the-effect-of-the-subdivision-level-on-the-geometry)

<!-- /TOC -->
---
A Blender based generator of tunnel systems and cave triangulations and point clouds  

Ribs is a mock up name for [Lyon fish-bones](./Doc/Lyon_Fish_Bones).

<img src="Doc/ScreenShots/cave_sub_4_grid_size_x_1_grid_size_y_1_triangulation_-_global_view_point_love_.png" alt="drawing" width="800"/>

## Requirements
* Python
* Blender version > 4.0.2

## Installation

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
```

## Exporting to ply

```
python export_to_ply.py -h
python export_to_ply.py -v --subdivision 3 --grid_size_x 3 --grid_size_y 2
```

Open the resulting file (`cave_*.ply`) e.g. with `https://point.love/`

## TODO
* Try the `apply_modifiers=True` exporting option.

## The Cave

### Different rendering tools

<figure>
  <img src="Doc/ScreenShots//cave_sub_2_grid_size_x_3_grid_size_y_2_point_cloud_-_mesh_lab.png" alt="drawing" width="800"/>
  <figcaption>MeshLab renderer on point cloud, subdivision=2, grid_size_x=3, grid_size_y=2</figcaption>
</figure>

<figure>
  <img src="Doc/ScreenShots/cave_sub_2_grid_size_x_3_grid_size_y_2_point_cloud_-_point_love.png" alt="drawing" width="800"/>
  <figcaption>Point.love renderer on point cloud, subdivision=2, grid_size_x=3, grid_size_y=2</figcaption>
</figure>

### Triangulation vs point cloud
<figure>
  <img src="Doc/ScreenShots/cave_sub_1_grid_size_x_1_grid_size_y_1_point_cloud_-_global_view_point_love.png" alt="drawing" width="800"/>
  <figcaption>Point cloud, subdivision=1</figcaption>
</figure>

<figure>
  <img src="Doc/ScreenShots/cave_sub_1_grid_size_x_1_grid_size_y_1_triangulation_-_global_view_point_love.png" alt="drawing" width="800"/>
  <figcaption>Triangulation, subdivision=1</figcaption>
</figure>

<figure>
  <img src="Doc/ScreenShots/cave_sub_2_grid_size_x_1_grid_size_y_1_point_cloud_-_global_view_point_love.png" alt="drawing" width="800"/>
  <figcaption>Point cloud, subdivision=2</figcaption>
</figure>

<figure>
  <img src="Doc/ScreenShots/cave_sub_2_grid_size_x_1_grid_size_y_1_triangulation_-_global_view_point_love.png" alt="drawing" width="800"/>
  <figcaption>Triangulation, subdivision=2</figcaption>
</figure>

### The effect of the subdivision level on the geometry

<figure>
  <img src="Doc/ScreenShots/cave_sub_1_grid_size_x_1_grid_size_y_1_triangulation_-_global_view_point_love_no_texture.png" alt="drawing" width="800"/>
  <figcaption>Triangulation, subdivision=1 (without color rendering)</figcaption>
</figure>

<figure>
  <img src="Doc/ScreenShots/cave_sub_2_grid_size_x_1_grid_size_y_1_triangulation_-_global_view_point_love_no_texture.png" alt="drawing" width="800"/>
  <figcaption>Triangulation, subdivision=2 (without color rendering)</figcaption>
</figure>

<figure>
  <img src="Doc/ScreenShots/cave_sub_3_grid_size_x_1_grid_size_y_1_triangulation_-_global_view_point_love_no_texture.png" alt="drawing" width="800"/>
  <figcaption>Triangulation, subdivision=3 (without color rendering)</figcaption>
</figure>

<figure>
  <img src="Doc/ScreenShots/cave_sub_4_grid_size_x_1_grid_size_y_1_triangulation_-_global_view_point_love_no_texture.png" alt="drawing" width="800"/>
  <figcaption>Triangulation, subdivision=4, with colors</figcaption>
</figure>

<figure>
  <img src="Doc/ScreenShots/cave_sub_3_grid_size_x_1_grid_size_y_1_triangulation_-_stalagtites_point_love_no_texture.png" alt="drawing" width="800"/>
  <figcaption>Triangulation, subdivision=4 (without color rendering)</figcaption>
</figure>

<figure>
  <img src="Doc/ScreenShots/cave_sub_4_grid_size_x_1_grid_size_y_1_triangulation_-_stalagatites_point_love.png" alt="drawing" width="800"/>
  <figcaption>Triangulation, subdivision=4, with colors</figcaption>
</figure>
