#### Implicit dependence towards https://github.com/VCityTeam/TunNetGen/
#
# The main part of this Dockerfile is dedicated to creating the context
# required for hosting the bpy python package. Because this concern is shared
# with the https://github.com/VCityTeam/TunNetGen/blob/master/docker/WithModeller/Dockerfile
# consider this code as a copy of the TunNetGen Dockerfile that should thus be
# used as reference. is a common concern
# with the https://github.com/VCityTeam/TunNetGen/

FROM python:3.10-slim

RUN apt-get update
RUN apt-get install -y git

# Provide bpy python module hidden dependencies, that is solve all the 
# ImportError one gets when running
#      python -c "import bpy"
RUN apt-get install -y libxrender1                    # for libXrender.so.1
RUN apt-get install -y mesa-utils libgl1-mesa-glx     # for libXxf86vm.so.1
RUN apt-get install -y libxi6                         # for libXi.so.6
RUN apt-get install -y libxkbcommon-x11-0             # for libxkbcommon.so.0
RUN apt-get install -y libgomp1                       # for libgomp.so.1
RUN apt-get install -y libsm6                         # for libSM.so.6

RUN pip3 install bpy

#############################################################################
# Here starts what specifically concerns RIBS
RUN git clone https://github.com/VCityTeam/TT-Ribs.git
WORKDIR TT-Ribs/Src
RUN git log -1
RUN chmod a+w /TT-Ribs/Src
RUN pip3 install git+https://github.com/VCityTeam/bpyhelpers.git@master
ENTRYPOINT [ "python" ]
