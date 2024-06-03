.PHONY: setup run init-letsencrypt clean

# Variables
DOMAIN ?= $(shell read -p "Ingresa tu dominio (deja vacío para configuración local): " domain && echo $$domain)
EMAIL ?= $(shell read -p "Ingresa tu correo electrónico para el certificado SSL: " email && echo $$email)
PROD_MODE ?= $(shell read -p "¿Modo producción? (s/n): " mode && echo $$mode)

# Convertir la respuesta del modo a local o producción
MODE := $(if $(findstring s,$(PROD_MODE)),production,local)

# Establecer valores predeterminados
DOMAIN := $(or $(DOMAIN),localhost)
EMAIL := $(or $(EMAIL),admin@localhost)

setup:
	# Instalar dependencias necesarias
	sudo apt-get update
	sudo apt-get install -y docker-ce docker-ce-cli containerd.io python3-pip python3-venv
	
	# Configurar entorno virtual
	python3 -m venv virtual_microscope/venv
	touch .env
	. virtual_microscope/venv/bin/activate && pip install --upgrade pip
	
	# Generar configuración de Nginx basada en el modo
	python3 scripts/generate_nginx_conf.py $(MODE) $(DOMAIN)

	# Construir imágenes Docker
	sudo docker compose build redis_vm db_vm gunicorn_vm daphne_vm celery_vm nginx_vm

	# Inicializar y configurar la base de datos PostgreSQL
	docker compose up --no-build -d redis_vm db_vm gunicorn_vm daphne_vm celery_vm nginx_vm
	docker compose exec gunicorn_vm python manage.py makemigrations
	docker compose exec gunicorn_vm python manage.py migrate
	
	# Crear superusuario
	@docker compose exec gunicorn_vm python manage.py shell < scripts/create_superuser.py

	# Solicitar y configurar certificados SSL si es producción
ifneq ($(MODE),local)
	make init-letsencrypt
endif

	# Iniciar la aplicación
	make run

init-letsencrypt:
	./init-letsencrypt.sh $(DOMAIN) $(EMAIL)

run:
	export DJANGO_SETTINGS_MODULE=settings
	docker compose up --no-build --no-recreate redis_vm db_vm gunicorn_vm daphne_vm celery_vm nginx_vm

migration:
	export DJANGO_SETTINGS_MODULE=virtual_microscope.virtual_microscope.settings
	docker compose up --no-build -d --no-recreate redis_vm db_vm gunicorn_vm daphne_vm celery_vm nginx_vm
	docker compose exec gunicorn_vm python manage.py makemigrations
	docker compose exec gunicorn_vm python manage.py migrate
	docker compose down

clean:
	docker compose down
	rm -rf docs/




# .PHONY: setup run init-letsencrypt clean

# setup:
# 	# Install necessary dependencies
# 	sudo apt-get update
# 	sudo apt-get install -y docker-ce docker-ce-cli containerd.io python3-pip python3-venv
	
# 	# Set up virtual environment
# 	python3 -m venv virtual_microscope/venv
# 	touch .env
# 	. virtual_microscope/venv/bin/activate && pip install --upgrade pip
	
# 	# Build Docker images
# 	sudo docker compose build redis_vm db_vm gunicorn_vm daphne_vm celery_vm nginx_vm

# 	# Initialize and configure PostgreSQL database
# 	docker compose up --no-build -d redis_vm db_vm gunicorn_vm daphne_vm celery_vm nginx_vm
# 	docker compose exec gunicorn_vm python manage.py makemigrations
# 	docker compose exec gunicorn_vm python manage.py migrate
	
# 	# Create superuser
# 	@docker compose exec gunicorn_vm python manage.py shell < scripts/create_superuser.py

# init-letsencrypt:
# 	./init-letsencrypt.sh

# run:
# 	export DJANGO_SETTINGS_MODULE=settings
# 	docker compose up --no-build --no-recreate redis_vm db_vm gunicorn_vm daphne_vm celery_vm nginx_vm

# migration:
# 	export DJANGO_SETTINGS_MODULE=virtual_microscope.virtual_microscope.settings
# 	docker compose up --no-build -d --no-recreate redis_vm db_vm gunicorn_vm daphne_vm celery_vm nginx_vm
# 	docker compose exec gunicorn_vm python manage.py makemigrations
# 	docker compose exec gunicorn_vm python manage.py migrate
# 	docker compose down

# clean:
# 	docker compose down
# 	rm -rf docs/
