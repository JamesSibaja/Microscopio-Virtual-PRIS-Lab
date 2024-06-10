#!/bin/bash

# Define los parámetros de entrada
domains=($1)
rsa_key_size=4096
data_path="./letsencrypt"
email=$2
staging=0 # Set to 1 if you're testing your setup to avoid hitting request limits

# Verifica que el script se esté ejecutando con privilegios de superusuario
if [[ "$EUID" -ne 0 ]]; then
  echo "Por favor, ejecuta el script con sudo."
  exit 1
fi

# Verifica si la carpeta existe y tiene permisos de escritura
if [ ! -d "$data_path" ]; then
  echo "La carpeta $data_path no existe. Creándola..."
  mkdir -p "$data_path"
fi

if [ ! -w "$data_path" ]; then
  echo "No tienes permisos de escritura en la carpeta $data_path. Por favor, ajusta los permisos."
  exit 1
fi

# Descarga los parámetros TLS recomendados si no existen
if [ ! -e "$data_path/conf/options-ssl-nginx.conf" ] || [ ! -e "$data_path/conf/ssl-dhparams.pem" ]; then
  echo "### Downloading recommended TLS parameters ..."
  mkdir -p "$data_path/conf"
  curl -s https://raw.githubusercontent.com/certbot/certbot/v2.11.0/certbot-nginx/certbot_nginx/_internal/tls_configs/options-ssl-nginx.conf > "$data_path/conf/options-ssl-nginx.conf"
  curl -s https://raw.githubusercontent.com/certbot/certbot/v2.11.0/certbot/certbot/ssl-dhparams.pem > "$data_path/conf/ssl-dhparams.pem"
  echo
fi

# Limpia cualquier certificado existente
echo "### Cleaning up any existing certificates for $domains ..."
docker compose run --rm --entrypoint "\
  rm -Rf /etc/letsencrypt/live/$domains && \
  rm -Rf /etc/letsencrypt/live/${domains}-0001 && \
  rm -Rf /etc/letsencrypt/archive/$domains && \
  rm -Rf /etc/letsencrypt/archive/${domains}-0001 && \
  rm -Rf /etc/letsencrypt/renewal/$domains.conf && \
  rm -Rf /etc/letsencrypt/renewal/${domains}-0001.conf" certbot
echo

# Asegúrate de que los directorios se han eliminado completamente
# Asegúrate de que los directorios se han eliminado completamente
echo "### Verifying cleanup ..."
cleanup_status=$(docker compose run --rm --entrypoint "\
  sh -c 'if [ -d /etc/letsencrypt/live/$domains ]; then echo \"/etc/letsencrypt/live/$domains still exists\"; fi; \
          if [ -d /etc/letsencrypt/archive/$domains ]; then echo \"/etc/letsencrypt/archive/$domains still exists\"; fi; \
          if [ -f /etc/letsencrypt/renewal/$domains.conf ]; then echo \"/etc/letsencrypt/renewal/$domains.conf still exists\"; fi; \
          if [ ! -d /etc/letsencrypt/live/$domains ] && [ ! -d /etc/letsencrypt/archive/$domains ] && [ ! -f /etc/letsencrypt/renewal/$domains.conf ]; then echo \"Cleanup verified.\"; exit 0; else exit 1; fi'" certbot)

echo "$cleanup_status"

if [[ "$cleanup_status" == *"still exists"* ]]; then
  echo "### Adjusting permissions and forcing cleanup of remaining files..."

  # Verifica si el directorio /etc/letsencrypt/live/demo-js.com existe antes de intentar ajustar los permisos y eliminar los archivos restantes
   if docker compose run --rm --entrypoint "test -d /etc/letsencrypt/live/$domains" certbot; then
    # Ajusta los permisos de los directorios y archivos restantes
    docker compose run --rm --entrypoint "\
      chmod -R 777 /etc/letsencrypt/live/$domains" certbot

    # Elimina los directorios y archivos restantes
    docker compose run --rm --entrypoint "\
      rm -rf /etc/letsencrypt/live/$domains" certbot
    echo

    echo "### Re-verifying cleanup..."
    cleanup_status=$(docker compose run --rm --entrypoint "\
      sh -c 'if [ -d /etc/letsencrypt/live/$domains ]; then echo \"/etc/letsencrypt/live/$domains still exists\"; fi; \
              if [ ! -d /etc/letsencrypt/live/$domains ]; then echo \"Cleanup verified.\"; exit 0; else exit 1; fi'" certbot)

    echo "$cleanup_status"

    if [[ "$cleanup_status" == *"still exists"* ]]; then
      echo "Cleanup verification failed again. Exiting."
      exit 1
    fi
  else
    echo "Directory /etc/letsencrypt/live/$domains does not exist. Exiting."
    exit 1
  fi

if docker compose run --rm --entrypoint "test -d /etc/letsencrypt/archive/$domains" certbot; then
    # Ajusta los permisos de los directorios y archivos restantes
    docker compose run --rm --entrypoint "\
      chmod -R 777 /etc/letsencrypt/archive/$domains" certbot

    # Elimina los directorios y archivos restantes
    docker compose run --rm --entrypoint "\
      rm -rf /etc/letsencrypt/archive/$domains" certbot
    echo

    echo "### Re-verifying cleanup..."
    cleanup_status=$(docker compose run --rm --entrypoint "\
      sh -c 'if [ -d /etc/letsencrypt/archive/$domains ]; then echo \"/etc/letsencrypt/archive/$domains still exists\"; fi; \
              [ ! -d /etc/letsencrypt/archive/$domains ]; then echo \"Cleanup verified.\"; exit 0; else exit 1; fi'" certbot)

    echo "$cleanup_status"

    if [[ "$cleanup_status" == *"still exists"* ]]; then
      echo "Cleanup verification failed again. Exiting."
      exit 1
    fi
  else
    echo "Directory /etc/letsencrypt/archive/$domains does not exist. Exiting."
    exit 1
  fi

if docker compose run --rm --entrypoint "test -d /etc/letsencrypt/renewal/$domains.conf" certbot; then
    # Ajusta los permisos de los directorios y archivos restantes
    docker compose run --rm --entrypoint "\
      chmod 777 /etc/letsencrypt/renewal/$domains.conf" certbot

    # Elimina los directorios y archivos restantes
    docker compose run --rm --entrypoint "\
      rm -f /etc/letsencrypt/renewal/$domains.conf" certbot
    echo

    echo "### Re-verifying cleanup..."
    cleanup_status=$(docker compose run --rm --entrypoint "\
      sh -c '
              if [ -f /etc/letsencrypt/renewal/$domains.conf ]; then echo \"/etc/letsencrypt/renewal/$domains.conf still exists\"; fi; \
              [ ! -f /etc/letsencrypt/renewal/$domains.conf ]; then echo \"Cleanup verified.\"; exit 0; else exit 1; fi'" certbot)

    echo "$cleanup_status"

    if [[ "$cleanup_status" == *"still exists"* ]]; then
      echo "Cleanup verification failed again. Exiting."
      exit 1
    fi
  else
    echo "Directory /etc/letsencrypt/renewal/$domains.conf does not exist. Exiting."
    exit 1
  fi

fi


echo

# Crea un certificado dummy si es necesario
if [ ! -e "$data_path/conf/live/$domains/privkey.pem" ]; then
  echo "### Creating dummy certificate for $domains ..."
  path="$data_path/conf/live/$domains"
  mkdir -p "$path"
  docker compose run --rm --entrypoint "\
    openssl req -x509 -nodes -newkey rsa:4096 -days 1\
      -keyout '/etc/letsencrypt/live/$domains/privkey.pem' \
      -out '/etc/letsencrypt/live/$domains/fullchain.pem' \
      -subj '/CN=localhost'" certbot
  echo
fi

# Inicia nginx
echo "### Starting nginx ..."
docker compose up --force-recreate -d nginx_vm
echo

# Elimina el certificado dummy
echo "### Deleting dummy certificate for $domains ..."
docker compose run --rm --entrypoint "\
  rm -Rf /etc/letsencrypt/live/$domains && \
  rm -Rf /etc/letsencrypt/live/${domains}-0001 && \
  rm -Rf /etc/letsencrypt/archive/$domains && \
  rm -Rf /etc/letsencrypt/archive/${domains}-0001 && \
  rm -Rf /etc/letsencrypt/renewal/$domains.conf && \
  rm -Rf /etc/letsencrypt/renewal/${domains}-0001.conf" certbot
echo

# Solicita un certificado de Let's Encrypt
echo "### Requesting Let's Encrypt certificate for $domains ..."
domain_args=""
for domain in "${domains[@]}"; do
  domain_args="$domain_args -d $domain"
done

email_arg="--email $email"
if [ -z "$email" ];then email_arg="--register-unsafely-without-email"; fi

staging_arg=""
if [ $staging != "0" ];then staging_arg="--staging"; fi

docker compose run --rm --entrypoint "\
  certbot certonly --webroot -w /var/www/certbot \
    $staging_arg \
    $email_arg \
    $domain_args \
    --rsa-key-size $rsa_key_size \
    --agree-tos \
    --force-renewal \
    -v" certbot
echo

# Recarga nginx
echo "### Reloading nginx ..."
docker compose exec nginx_vm nginx -s reload
