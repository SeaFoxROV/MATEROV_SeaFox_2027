#!/usr/bin/env bash
xhost +

sudo docker rm -f seafox_pilot_container 2>/dev/null

sudo docker run -it --name seafox_pilot_container \
  -v "$(cd .. && pwd)/pilot_ws":/home/ros/ros2_ws \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  -v /dev/input:/dev/input \
  -v /run/udev:/run/udev:ro \
  -e DISPLAY=$DISPLAY \
  -e SDL_AUDIODRIVER=dummy \
  --device-cgroup-rule='c 13:* rmw' \
  --group-add "$(getent group input | cut -d: -f3)" \
  --network host \
  seafox-pilot
