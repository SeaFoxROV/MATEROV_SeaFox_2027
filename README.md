# Comandos útiles ROV

Guía rápida de comandos para configurar la red, el contenedor Docker y ROS 2.

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

## Red

### Ver interfaces de red
Lista las interfaces de red y su estado. Útil para confirmar que la conexión con la ESP32 está activa.

```bash
ip link show
```
