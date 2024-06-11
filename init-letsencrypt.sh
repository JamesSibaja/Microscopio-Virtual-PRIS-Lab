#!/bin/bash

# Define los parámetros de entrada
domains=$1
email=$2
data_path="./letsencrypt"
staging=0 # Set to 1 if you're testing your setup to avoid hitting request limits

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

# Seleccionar ZeroSSL como el CA predeterminado
$HOME/.acme.sh/acme.sh --set-default-ca --server https://acme.zerossl.com/v2/DV90

# Crear directorio para los certificados del dominio
mkdir -p $data_path/live/$domains/

# Obtener certificados
echo "### Solicitando certificados para $domains ..."
$HOME/.acme.sh/acme.sh --issue --webroot "$data_path/www" -d "$domains" --email "$email" --force --log

# Verifica si el proceso de emisión fue exitoso
if [ $? -ne 0 ]; then
  echo "Error al solicitar certificados para $domains"
  exit 1
fi

# Instalar certificados en las rutas correspondientes
$HOME/.acme.sh/acme.sh --install-cert -d $domains \
  --key-file $data_path/live/$domains/privkey.pem \
  --fullchain-file $data_path/live/$domains/fullchain.pem \
  --reloadcmd "sudo docker compose exec nginx_vm nginx -s reload"

# Verifica si el proceso de instalación fue exitoso
if [ $? -ne 0 ]; then
  echo "Error al instalar certificados para $domains"
  exit 1
fi

# Recargar nginx
echo "### Recargando nginx ..."
docker compose exec nginx_vm nginx -s reload
