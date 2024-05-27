# Microscopio-Virtual-PRIS-Lab-B77342
Este es el repositorio virtual del microscopio virtual del PRIS-Lab de la Escuela de Ingeniría Eléctrica de la UCR

## Requisitos previos

Para desplegar esta plataforma en tu servidor local, asegúrate de tener instalados los siguientes programas:

- makefile
- git
- Docker
- Docker Compose

## Instalación

Para comenzar, clona este repositorio utilizando el siguiente comando:

```bash
git clone https://github.com/JamesSibaja/Microscopio-Virtual-PRIS-Lab-B77342.git
```

Luego, dirígete al directorio principal del repositorio:

```bash
cd Microscopio-Virtual-PRIS-Lab-B77342
```

## Despliegue en servidor local

Para desplegar la plataforma en tu servidor local, ejecuta el siguiente comando:

```bash
sudo make setup
```

## Despliegue en servidor

Si deseas desplegar la plataforma en un servidor, primero asegúrate de editar el archivo nginx.conf según tus necesidades. Luego, ejecuta el siguiente comando:

```bash
sudo make setup
```

## Información adicional

Este sistema ha sido probado en Ubuntu 23.04.
