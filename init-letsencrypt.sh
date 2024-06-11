#!/bin/bash

# Define los parámetros de entrada
domains=$1
email=$2
staging=$3 # Cambia a 1 para usar el servidor de pruebas de Let's Encrypt
data_path="./letsencrypt"

# Verifica que el script se esté ejecutando con privilegios de superusuario
if [[ "$EUID" -ne 0 ]]; then
  echo "Por favor, ejecuta el script con sudo."
  exit 1
fi

# Verifica si la carpeta existe y tiene permisos de escritura
if [ ! -d "$data_path" ]; then
  mkdir -p "$data_path"
fi

# Cargar acme.sh en el PATH
export PATH="$HOME/.acme.sh":$PATH

# Instalar acme.sh si no está instalado
if [ ! -d "$HOME/.acme.sh" ]; then
  echo "### Instalando acme.sh ..."
  curl https://get.acme.sh | sh
  source ~/.bashrc
fi

# Seleccionar el servidor CA basado en el entorno de pruebas o producción
if [ "$staging" != "0" ]; then
  echo "### Usando el entorno de pruebas de Let's Encrypt ..."
  server="https://acme-staging-v02.api.letsencrypt.org/directory"
else
  echo "### Usando el entorno de producción de Let's Encrypt ..."
  server="https://acme-v02.api.letsencrypt.org/directory"
fi

# Configurar acme.sh para usar el servidor seleccionado
$HOME/.acme.sh/acme.sh --set-default-ca --server "$server"

# Verificar y crear directorios necesarios
mkdir -p "$data_path/live/$domains/"
mkdir -p "$data_path/www"
mkdir -p "/etc/ssl/certs"

# Configuración temporal de Nginx
echo "### Configurando Nginx temporalmente para validar $domains ..."
# python generate_nginx_conf.py local "$domains"
# sudo docker cp nginx.conf nginx_vm:/etc/nginx/nginx.conf
sudo docker compose exec nginx_vm nginx -s reload

# Obtener certificados
echo "### Solicitando certificados para $domains ..."
$HOME/.acme.sh/acme.sh --issue --webroot "$data_path/www" -d "$domains" --email "$email" --force --log

if [ $? -ne 0 ]; then
  echo "### Error al obtener certificados para $domains ..."
  exit 1
fi

echo "### Certificados obtenidos con éxito para $domains ..."

# Instalar certificados en las rutas correspondientes
$HOME/.acme.sh/acme.sh --install-cert -d $domains \
  --key-file $data_path/live/$domains/privkey.pem \
  --fullchain-file $data_path/live/$domains/fullchain.pem \
  --reloadcmd "sudo docker compose exec nginx_vm nginx -s reload"

# Configuración final de Nginx
echo "### Configurando Nginx con SSL para $domains ..."
python generate_nginx_conf.py prod "$domains"
sudo docker cp nginx.conf nginx_vm:/etc/nginx/nginx.conf
sudo docker compose exec nginx_vm nginx -s reload

echo "### Todo listo!"
