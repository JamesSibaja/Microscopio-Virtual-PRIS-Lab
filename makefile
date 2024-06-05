.PHONY: setup run init-letsencrypt clean

setup:
	# Ejecutar script de configuración
	sudo chmod +x ./init-letsencrypt.sh
	bash setup.sh

init-letsencrypt:
	sudo chmod +x ./init-letsencrypt.sh
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

# .PHONY: setup run

# setup:
#  	# sudo apt-get install docker-ce docker-ce-cli containerd.io
# 	export DJANGO_SETTINGS_MODULE=settings
# 	mkdir -p virtual_microscope/media/slide virtual_microscope/media/archivo
# 	mkdir -p virtual_microscope/venv/
# 	sudo apt-get install python3-pip
# 	sudo apt-get install python3-venv
# 	python3 -m venv virtual_microscope/venv
# 	touch .env
# 	. virtual_microscope/venv/bin/activate && pip install --upgrade pip
	
# 	sudo docker compose build  redis_vm db_vm gunicorn_vm daphne_vm celery_vm nginx_vm

#     # Iniciar y configurar las bases de datos PostgreSQL
# 	docker compose up --no-build -d --no-recreate  redis_vm db_vm gunicorn_vm daphne_vm celery_vm nginx_vm

	
# 	docker compose exec gunicorn_vm python manage.py makemigrations
# 	docker compose exec gunicorn_vm python manage.py migrate
# 	sleep 10
	
#     # Crear un superusuario (cambiar los valores de acuerdo a tus necesidades) 
# 	# docker compose exec gunicorn_vm python manage.py createsuperuser --username=postgres --email=jsibajagranados2@gmail.com
# 	@docker compose exec gunicorn_vm python manage.py shell -c "from django.contrib.auth.models import User; from getpass import getpass; username='postgres'; email='jsibajagranados2@gmail.com'; password=getpass('Enter password for superuser: '); User.objects.create_superuser(username, email, password) if not User.objects.filter(username=username).exists() else print('Superuser already exists')"

	
# init-docs: # docker compose run documentation make -C virtual_microscope/docs html
# 	if [ ! -d "./docs" ]; then \
#         mkdir docs; \
# 		. virtual_microscope/venv/bin/activate && pip install --upgrade pip; \
# 		pip install -U sphinx; \
#         cd docs && sphinx-quickstart; \
#     fi
# 	sudo docker compose build documentation_vm 

# generate-docs:
# 	docker compose up --no-build -d --no-recreate documentation_vm 
# 	# docker compose exec documentation_vm make -C /app/docs html
# 	cd ./docs/build/html && python3 -m http.server 8080

# generate-pdf: generate-docs
# 	docker compose run documentation make -C virtual_microscope/docs latexpdf


# run:
# 	export DJANGO_SETTINGS_MODULE=settings
# 	docker compose up --no-build --no-recreate redis_vm db_vm gunicorn_vm daphne_vm celery_vm nginx_vm
# migration:
# 	export DJANGO_SETTINGS_MODULE=virtual_microscope.virtual_microscope.settings
# 	docker compose up --no-build -d --no-recreate  redis_vm db_vm gunicorn_vm daphne_vm celery_vm nginx_vm
# 	docker compose exec gunicorn_vm python manage.py makemigrations
# 	docker compose exec gunicorn_vm python manage.py migrate
# 	docker compose down

# clean:
# 	docker compose down
# 	rm -rf docs/