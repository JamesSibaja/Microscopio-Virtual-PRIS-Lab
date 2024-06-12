#!/bin/bash

# Preguntar por el modo de operación
read -p "¿Modo producción? (s/n): " mode
read -p "Ingresa tu dominio (deja vacío para configuración local): " domain
read -p "Ingresa tu correo electrónico para el certificado SSL: " email
read -s -p "Ingresa la contraseña del superusuario de Django: " password
echo

# Determinar el modo
if [[ $mode == "s" || $mode == "S" ]]; then
    MODE="prod"
else
    MODE="local"
fi

# Establecer valores predeterminados
DOMAIN=${domain:-localhost}
EMAIL=${email:-admin@localhost}
PASSWORD=$password

# Configurar entorno virtual
python3 -m venv virtual_microscope/venv
source virtual_microscope/venv/bin/activate

# Instalar pip y dependencias
pip install --upgrade pip --break-system-packages
pip install -r requirements.txt

# Generar configuración de Nginx
python scripts/generate_nginx_conf.py $MODE $DOMAIN

# Asegúrate de que los archivos de configuración existan
if [[ ! -f nginx.conf ]]; then
    echo "Error: Los archivos de configuración de Nginx no se generaron correctamente."
    exit 1
fi

# Exportar la variable de modo para docker-compose
export MODE=$MODE

if [[ $MODE == "prod" ]]; then
    if [ ! -f /etc/ssl/certs/dhparam.pem ]; then
        echo "### Generating dhparam.pem file ..."
        sudo openssl dhparam -out /etc/ssl/certs/dhparam.pem 2048
    fi
fi

# Instalar acme.sh si no está instalado
if [ ! -d "$HOME/.acme.sh" ]; then
  echo "### Instalando acme.sh ..."
  curl https://get.acme.sh | sh
fi

# Cargar acme.sh en el PATH
export PATH="$HOME/.acme.sh":$PATH

# Construir imágenes Docker
sudo docker compose build --build-arg MODE=$MODE redis_vm db_vm gunicorn_vm daphne_vm celery_vm nginx_vm

# Inicializar y configurar la base de datos PostgreSQL
sudo docker compose up --no-build -d --no-recreate redis_vm db_vm gunicorn_vm daphne_vm celery_vm
sudo docker compose exec gunicorn_vm python manage.py makemigrations
sudo docker compose exec gunicorn_vm python manage.py migrate

# Exportar las variables de entorno para el superusuario
export DJANGO_SUPERUSER_EMAIL=$EMAIL
export DJANGO_SUPERUSER_PASSWORD=$PASSWORD

sudo docker exec -e DJANGO_SUPERUSER_EMAIL=$DJANGO_SUPERUSER_EMAIL -e DJANGO_SUPERUSER_PASSWORD=$DJANGO_SUPERUSER_PASSWORD $(sudo docker ps -q -f name=gunicorn_vm) python manage.py shell -c "exec(open('/app/scripts/create_superuser.py').read())"

# Iniciar Nginx sin SSL
sudo docker compose up --no-build -d --no-recreate nginx_vm

if [[ $MODE == "prod" ]]; then
    sudo ./init-letsencrypt.sh $DOMAIN $EMAIL
    # Regenerar configuración de Nginx para SSL
    python scripts/generate_nginx_conf.py $MODE $DOMAIN --with-ssl
fi

# Iniciar la aplicación
sudo docker compose up --no-build -d --no-recreate redis_vm db_vm gunicorn_vm daphne_vm celery_vm nginx_vm

# Recargar Nginx con la nueva configuración
if [[ $MODE == "prod" ]]; then
    sudo docker compose exec nginx_vm nginx -s reload
fi