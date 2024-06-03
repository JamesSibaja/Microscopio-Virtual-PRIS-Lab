FROM nginx:latest

COPY ./nginx_local.conf /etc/nginx/conf.d/nginx_local.conf
COPY ./nginx_prod.conf /etc/nginx/conf.d/nginx_prod.conf

RUN mkdir -p /var/www/certbot
