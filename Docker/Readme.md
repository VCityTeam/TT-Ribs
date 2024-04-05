# Using the Blender based examples with docker 
<!-- TOC -->

- [Building the docker image](#building-the-docker-image)
  - [Building without cloning](#building-without-cloning)
  - [Building after cloning](#building-after-cloning)
- [Running things](#running-things)
- [A short list of working examples](#a-short-list-of-working-examples)
- [Debugging the container](#debugging-the-container)

<!-- /TOC -->

## Building the docker image

### Building without cloning

```bash
docker build -t vcity/ribs https://github.com/VCityTeam/TT-Ribs.git -f Docker/Dockerfile
```

### Building after cloning

From the root folder of the project
```bash
git clone https://github.com/VCityTeam/TT-Ribs.git
cd TunNetGen
docker build -t vcity/ribs Docker
```

## Running things

In order to obtain the flags/options of e.g. the cylinder example one can run

```bash
docker run -i --rm vcity/ribs export_to_ply.py -h
```

In order to obtain the resulting PLY format files, you must provide an the 
`--outputdir` flag with an argument that matches the mounted volume e.g.

```bash
docker run --rm -v $(pwd)/data:/Output vcity/ribs export_to_ply.py --subdivision 3 --outputdir /Output
```

that should create a `data/` directory within the invocation directory with
the expected `PLY` format files.

## A short list of working examples

```bash
docker run --rm -v $(pwd)/data:/Output vcity/ribs export_to_ply.py --subdivision 2 --grid_size_x 3 --grid_size_y 2 --outputdir /Output 
```

## Debugging the container
If you want to check the container state, you can run
```bash
docker run --rm -it --entrypoint bash vcity/ribs
```
