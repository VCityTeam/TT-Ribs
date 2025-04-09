# Using the Blender based examples with docker<!-- omit from toc -->

## Table Of Content<!-- omit from toc -->
<!-- TOC -->

- [Building the docker image](#building-the-docker-image)
  - [Building without cloning](#building-without-cloning)
  - [Building after cloning](#building-after-cloning)
- [Running the `Cave` generator](#running-the-cave-generator)
  - [Obtaining the usage instructions](#obtaining-the-usage-instructions)
  - [Retrieving the generated `PLY` files](#retrieving-the-generated-ply-files)
  - [A short list of working examples](#a-short-list-of-working-examples)
- [Running the `Tunnel` generator](#running-the-tunnel-generator)
  - [Obtaining the usage instructions](#obtaining-the-usage-instructions-1)
  - [Retrieving the generated `PLY` files](#retrieving-the-generated-ply-files-1)
  - [A short list of working examples](#a-short-list-of-working-examples-1)
- [Debugging the container](#debugging-the-container)

<!-- /TOC -->

## Building the docker image

### Building without cloning

```bash
docker build -t vcity/ribs https://github.com/VCityTeam/TT-Ribs.git -f Docker/Dockerfile
```

:warning: if you are running on arch different from amd64 and you get the following error message
```
Ignored the following versions that require a different python version: 2.82.1 Requires-Python >=3.7, <3.8                                         
0.845 ERROR: Could not find a version that satisfies the requirement bpy
```

then you will have to cross build for the amd64 arch that is use

```bash
docker buildx build --platform linux/amd64 -t vcity/ribs https://github.com/VCityTeam/TT-Ribs.git -f Docker/Dockerfile
```

### Building after cloning

From the root folder of the project

```bash
git clone https://github.com/VCityTeam/TT-Ribs.git
cd TT-Ribs
docker build -t vcity/ribs Docker
```

## Running the `Cave` generator

### Obtaining the usage instructions

In order to obtain the flags/options of the `Cave` one can run

```bash
docker run -i --rm vcity/ribs Cave.py -h
```

### Retrieving the generated `PLY` files

When using docker as runtime, and in order to obtain the resulting PLY
format files, you must provide an the
`--outputdir` flag with an argument that matches the mounted volume e.g.

```bash
docker run --rm -v $(pwd)/data:/Output vcity/ribs Cave.py --subdivision 3 --outputdir /Output
```

that should create a `data/` directory within the invocation directory with
the expected `PLY` format files.

### A short list of working examples

```bash
docker run --rm -v $(pwd)/data:/Output vcity/ribs Cave.py --subdivision 2 --grid_size_x 3 --grid_size_y 2 --outputdir /Output
```

## Running the `Tunnel` generator

Except for some run time flags, the usage of `Tunnel` generator is quite
similar to the `Cave` generator usage.

### Obtaining the usage instructions

In order to obtain the flags/options of the `Tunnel` generator one can run

```bash
docker run -i --rm vcity/ribs Tunnel.py -h
```

### Retrieving the generated `PLY` files

When using docker as runtime, and in order to obtain the resulting PLY
format files, you must provide an the
`--outputdir` flag with an argument that matches the mounted volume e.g.

```bash
docker run --rm -v $(pwd)/data:/Output vcity/ribs Tunnel.py --outputdir /Output
```

that should create a `data/` directory within the invocation directory with
the expected `PLY` format files.

### A short list of working examples

```bash
docker run --rm -v $(pwd)/data:/Output vcity/ribs Tunnel.py --subdivision 2 --outputdir /Output
```

```bash
docker run --rm -v $(pwd)/data:/Output vcity/ribs Tunnel.py --subdivision 3 --outputdir /Output
```

## Debugging the container

If you want to check the container state, you can run

```bash
docker run --rm -it --entrypoint bash vcity/ribs
```
