.PHONY: setup run init-letsencrypt clean

setup:
	# Install necessary dependencies
	sudo apt-get update
	sudo apt-get install -y docker-ce docker-ce-cli containerd.io python3-pip python3-venv
	
	# Set up virtual environment
	python3 -m venv virtual_microscope/venv
	touch .env
	. virtual_microscope/venv/bin/activate && pip install --upgrade pip
	
	# Build Docker images
	sudo docker compose build redis_vm db_vm gunicorn_vm daphne_vm celery_vm nginx_vm

	# Initialize and configure PostgreSQL database
	docker compose up --no-build -d redis_vm db_vm gunicorn_vm daphne_vm celery_vm nginx_vm
	docker compose exec gunicorn_vm python manage.py makemigrations
	docker compose exec gunicorn_vm python manage.py migrate
	
	# Create superuser
	@docker compose exec gunicorn_vm python manage.py shell < scripts/create_superuser.py

init-letsencrypt:
	./init-letsencrypt.sh

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
