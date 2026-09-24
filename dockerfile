# CREATE DOCKER IMAGE
# docker build -t <image_name> --build-arg INSTALL_GAZEBO=true .
# CREATE DOCKER CONTAINER
# docker run -it --name <container_name> -v $PWD:/home/ros/ros2_ws -v /tmp/.X11-unix:/tmp/.X11-unix -e DISPLAY=$DISPLAY --network host <image_name>
FROM osrf/ros:humble-desktop AS base
ARG USERNAME=ros
ARG USER_UID=1000
ARG USER_GID=$USER_UID
ENV DEBIAN_FRONTEND=noninteractive

RUN groupadd --gid $USER_GID $USERNAME \
 && useradd -m -s /bin/bash --uid $USER_UID --gid $USER_GID $USERNAME \
 && apt-get update && apt-get install -y \
    sudo \
    python3-pip \
    python3-dev \
    ros-dev-tools \
    ros-humble-teleop-twist-keyboard \
    xterm \
 && echo "$USERNAME ALL=(root) NOPASSWD:ALL" > /etc/sudoers.d/$USERNAME \
 && chmod 0440 /etc/sudoers.d/$USERNAME \
 && rm -rf /var/lib/apt/lists/*

RUN echo "source /opt/ros/humble/setup.bash" >> /home/$USERNAME/.bashrc \
 && echo "[ -f ~/ros2_ws/install/setup.bash ] && source ~/ros2_ws/install/setup.bash" >> /home/$USERNAME/.bashrc \
 && echo "alias cb='colcon build --symlink-install && source install/setup.bash'" >> /home/$USERNAME/.bashrc \
 && echo "alias sb='source ~/ros2_ws/install/setup.bash'" >> /home/$USERNAME/.bashrc \
 && mkdir -p /home/$USERNAME/ros2_ws \
 && chown -R $USER_UID:$USER_GID /home/$USERNAME

USER $USERNAME
WORKDIR /home/$USERNAME/ros2_ws
CMD ["bash"]

# ---------- simulación ----------
FROM base AS sim
USER root
RUN apt-get update && apt-get install -y \
    ros-humble-ros-gz \
    mesa-utils \
 && rm -rf /var/lib/apt/lists/* \
 && mkdir -p /tmp/runtime-ros && chmod 700 /tmp/runtime-ros \
 && chown $USER_UID:$USER_GID /tmp/runtime-ros
ENV QT_QPA_PLATFORM=xcb
ENV XDG_RUNTIME_DIR=/tmp/runtime-ros
USER $USERNAME
