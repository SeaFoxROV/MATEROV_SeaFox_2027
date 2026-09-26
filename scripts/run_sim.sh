#!/usr/bin/env bash
xhost +local:docker

docker run -it --rm --name sim_container \
  -e DISPLAY=$DISPLAY \
  -e QT_X11_NO_MITSHM=1 \
  -e QT_QPA_PLATFORM=xcb \
  -e XDG_RUNTIME_DIR=/tmp/runtime-ros \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  -v "$PWD":/home/ros/ros2_ws \
  --device /dev/dri \
  --group-add video \
  --group-add "$(stat -c '%g' /dev/dri/renderD128)" \
  seafox-sim
