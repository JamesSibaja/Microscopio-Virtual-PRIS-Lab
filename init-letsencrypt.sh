#!/bin/bash

domains=($1)
rsa_key_size=4096
data_path="./letsencrypt"
email=$2
staging=0 # Set to 1 if you're testing your setup to avoid hitting request limits

# Download recommended TLS parameters if they don't exist
if [ ! -e "$data_path/conf/options-ssl-nginx.conf" ] || [ ! -e "$data_path/conf/ssl-dhparams.pem" ]; then
  echo "### Downloading recommended TLS parameters ..."
  mkdir -p "$data_path/conf"
  curl -s https://raw.githubusercontent.com/certbot/certbot/v2.11.0/certbot-nginx/certbot_nginx/_internal/tls_configs/options-ssl-nginx.conf > "$data_path/conf/options-ssl-nginx.conf"
  curl -s https://raw.githubusercontent.com/certbot/certbot/v2.11.0/certbot/certbot/ssl-dhparams.pem > "$data_path/conf/ssl-dhparams.pem"
  echo
fi

# Clean up any existing certificates
echo "### Cleaning up any existing certificates for $domains ..."
docker compose run --rm --entrypoint "\
  rm -Rf /etc/letsencrypt/live/$domains && \
  rm -Rf /etc/letsencrypt/live/${domains}-0001 && \
  rm -Rf /etc/letsencrypt/archive/$domains && \
  rm -Rf /etc/letsencrypt/archive/${domains}-0001 && \
  rm -Rf /etc/letsencrypt/renewal/$domains.conf && \
  rm -Rf /etc/letsencrypt/renewal/${domains}-0001.conf" certbot
echo

# Ensure directories are completely removed
echo "### Verifying cleanup ..."
docker compose run --rm --entrypoint "sh -c '\
  if [ -d /etc/letsencrypt/live/$domains ] || [ -d /etc/letsencrypt/archive/$domains ] || [ -f /etc/letsencrypt/renewal/$domains.conf ]; then \
    echo \"Previous certificates not fully removed. Aborting.\"; exit 1; \
  fi'" certbot
if [ $? -ne 0 ]; then
  echo "Cleanup verification failed. Exiting."
  exit 1
fi
echo

# Create a dummy certificate if needed
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

# Start nginx
echo "### Starting nginx ..."
docker compose up --force-recreate -d nginx_vm
echo

# Delete the dummy certificate
echo "### Deleting dummy certificate for $domains ..."
docker compose run --rm --entrypoint "\
  rm -Rf /etc/letsencrypt/live/$domains && \
  rm -Rf /etc/letsencrypt/live/${domains}-0001 && \
  rm -Rf /etc/letsencrypt/archive/$domains && \
  rm -Rf /etc/letsencrypt/archive/${domains}-0001 && \
  rm -Rf /etc/letsencrypt/renewal/$domains.conf && \
  rm -Rf /etc/letsencrypt/renewal/${domains}-0001.conf" certbot
echo

# Request Let's Encrypt certificate
echo "### Requesting Let's Encrypt certificate for $domains ..."
domain_args=""
for domain in "${domains[@]}"; do
  domain_args="$domain_args -d $domain"
done

email_arg="--email $email"
if [ -z "$email" ]; then email_arg="--register-unsafely-without-email"; fi

staging_arg=""
if [ $staging != "0" ]; then staging_arg="--staging"; fi

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

# Reload nginx
echo "### Reloading nginx ..."
docker compose exec nginx_vm nginx -s reload
