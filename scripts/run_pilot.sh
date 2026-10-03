#!/usr/bin/env bash
xhost +

sudo docker run -it --name seafox_pilot_container \
  -v "$(cd .. && pwd)/pilot_ws":/home/ros/ros2_ws \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  -e DISPLAY=$DISPLAY \
  --network host \
  seafox-pilot
