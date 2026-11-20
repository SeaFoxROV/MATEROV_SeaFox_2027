# Comandos útiles ROV

Guía rápida de comandos para configurar la red, el contenedor Docker, ROS 2 y las cámaras.

## Configuración inicial (ejecutar una sola vez)

### Dar permisos a los scripts
Da permisos de ejecución a todos los scripts `.sh`. Se corre dentro de la carpeta de scripts.

```bash
chmod +x *.sh
```

### Configurar IP estática para la ESP32
Crea una conexión Ethernet con IP estática para comunicarse con la ESP32.

```bash
sudo nmcli connection add type ethernet con-name rov-eth mac 68:e4:3b:30:bd:3c ip4 192.168.1.10/24
```

## Docker

### Iniciar el contenedor
Arranca el contenedor ya creado.

```bash
sudo docker start <nombre_contenedor>
```

### Entrar al contenedor
Abre una terminal bash dentro del contenedor (una vez que ya está iniciado).

```bash
sudo docker exec -it <nombre_contenedor> bash
```

## ROS 2

### Compilar el workspace

```bash
cb  # alias de: colcon build --symlink-install && source install/setup.bash
```

### Lanzar un launch file
Ejecuta un launch file de un paquete.

```bash
ros2 launch <nombre_paquete> <nombre_launch_file>
```

### Ver lista de tópicos
Muestra todos los tópicos activos.

```bash
ros2 topic list
```

### Ver contenido de un tópico
Muestra en tiempo real los mensajes que se publican en un tópico.

```bash
ros2 topic echo <topico>
```

## Simulación

La simulación usa dos contenedores que se comunican por ROS 2 (ambos con `--network host`):
el de simulación (Gazebo + bridge) y el del piloto (joystick -> PWM -> empuje).

### 1. Abrir la piscina con el ROV (contenedor de simulación)
Desde la carpeta `scripts/`, inicia el contenedor de simulación:

```bash
./run_sim.sh
```

```bash
~/ros2_ws/launch_pool.sh
```

### 2. Mandar comandos de movimiento desde ROS 2 (contenedor del piloto)
En otra terminal, desde la carpeta `scripts/`, inicia el contenedor del piloto:

```bash
./run_pilot.sh
```


```bash
cd ~/ros2_ws
cb
ros2 launch pilot_pkg sim.launch.py
```

```bash
ros2 topic echo /model/seafox_rov/joint/thruster_0_joint/cmd_thrust
```

## Cámaras

### Ejecutar old_cameras
Entra a la carpeta `old_cameras` y ejecuta la ventana principal de la interfaz de cámaras.

```bash
python3 main_window.py
```

### Probar conectividad con las cámaras

```bash
ping <ip_camara>
```

## Red

### Ver interfaces de red
Lista las interfaces de red y su estado. Útil para confirmar que la conexión con la ESP32 está activa.

```bash
ip link show
```
