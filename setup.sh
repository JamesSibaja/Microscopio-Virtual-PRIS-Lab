#!/bin/bash

# Preguntar por el modo de operación
read -p "¿Modo producción? (s/n): " mode
read -p "Ingresa tu dominio (deja vacío para configuración local): " domain
read -p "Ingresa tu correo electrónico para el certificado SSL: " email

# Determinar el modo
if [[ $mode == "s" || $mode == "S" ]]; then
    MODE="production"
else
    MODE="local"
fi

# Establecer valores predeterminados
DOMAIN=${domain:-localhost}
EMAIL=${email:-admin@localhost}

# Configurar entorno virtual
python3 -m venv virtual_microscope/venv
source virtual_microscope/venv/bin/activate

# Instalar pip y dependencias
pip install --upgrade pip --break-system-packages
pip install -r requirements.txt

# Generar configuración de Nginx
python scripts/generate_nginx_conf.py $MODE $DOMAIN

# Asegúrate de que los archivos de configuración existan
if [[ ! -f nginx_local.conf || ! -f nginx_prod.conf ]]; then
    echo "Error: Los archivos de configuración de Nginx no se generaron correctamente."
    exit 1
fi

# Exportar la variable de modo para docker-compose
export MODE=$MODE

# Construir imágenes Docker
sudo docker compose build --build-arg MODE=$MODE redis_vm db_vm gunicorn_vm daphne_vm celery_vm nginx_vm

# Inicializar y configurar la base de datos PostgreSQL
sudo docker compose up --no-build -d --no-recreate redis_vm db_vm gunicorn_vm daphne_vm celery_vm nginx_vm
sudo docker compose exec gunicorn_vm python manage.py makemigrations
sudo docker compose exec gunicorn_vm python manage.py migrate

# Crear superusuario
sudo docker compose exec gunicorn_vm python manage.py shell < scripts/create_superuser.py

# Solicitar y configurar certificados SSL si es producción
if [[ $MODE == "production" ]]; then
    ./init-letsencrypt.sh $DOMAIN $EMAIL
fi

# Iniciar la aplicación
sudo docker compose up --no-build -d --no-recreate redis_vm db_vm gunicorn_vm daphne_vm celery_vm nginx_vm
