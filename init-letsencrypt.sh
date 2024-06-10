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
  mkdir -p "$data_path"
fi

# Cargar acme.sh en el PATH
export PATH="$HOME/.acme.sh":$PATH

# Obtener o renovar certificados
if [ -d "$data_path/live/$domains" ]; then
  echo "### Certificados existentes para $domains encontrados..."
else
  echo "### Solicitando certificados para $domains ..."
  $HOME/.acme.sh/acme.sh --issue --webroot "$data_path/www" -d "$domains" --email "$email" --rsa-key-size $rsa_key_size --force
fi

# Instalar certificados en las rutas correspondientes
$HOME/.acme.sh/acme.sh --install-cert -d $domains \
  --key-file $data_path/live/$domains/privkey.pem \
  --fullchain-file $data_path/live/$domains/fullchain.pem \
  --reloadcmd "sudo docker compose exec nginx_vm nginx -s reload"
