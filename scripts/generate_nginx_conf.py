import sys

def generate_nginx_conf(mode, domain):
    if mode == 'local':
        conf = f"""
        client_max_body_size 150G;
        proxy_read_timeout 600s;

        upstream django_app {{
            server gunicorn_vm:8765;
        }}

        upstream daphne_app {{
            server daphne_vm:8089;
        }}

        server {{
            listen 0.0.0.0:80;
            server_name _;

            location / {{
                proxy_pass http://django_app;
                proxy_http_version 1.1;
                proxy_set_header Upgrade $http_upgrade;
                proxy_set_header Connection $http_upgrade;
                proxy_set_header Host $host;
                proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
                proxy_redirect off;
            }}

            location /ws/ {{
                proxy_pass http://daphne_app;
                proxy_http_version 1.1;
                proxy_set_header Upgrade $http_upgrade;
                proxy_set_header Connection "upgrade";
                proxy_set_header Host $host;
            }}

            location /static/ {{
                alias /app/static/;
            }}

            location /media/ {{
                alias /app/media/;
            }}
        }}
        """
    elif mode == 'production':
        conf = f"""
        client_max_body_size 150G;
        proxy_read_timeout 600s;

        upstream django_app {{
            server gunicorn_vm:8765;
        }}

        upstream daphne_app {{
            server daphne_vm:8089;
        }}

        server {{
            listen 80;
            server_name {domain};

            location / {{
                proxy_pass http://django_app;
                proxy_http_version 1.1;
                proxy_set_header Upgrade $http_upgrade;
                proxy_set_header Connection $http_upgrade;
                proxy_set_header Host $host;
                proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
                proxy_redirect off;
            }}

            location /ws/ {{
                proxy_pass http://daphne_app;
                proxy_http_version 1.1;
                proxy_set_header Upgrade $http_upgrade;
                proxy_set_header Connection "upgrade";
                proxy_set_header Host $host;
            }}

            location /static/ {{
                alias /app/static/;
            }}

            location /media/ {{
                alias /app/media/;
            }}

            location /.well-known/acme-challenge/ {{
                root /var/www/certbot;
            }}

            location / {{
                return 301 https://$host$request_uri;
            }}
        }}

        server {{
            listen 443 ssl;
            server_name {domain};

            ssl_certificate /etc/letsencrypt/live/{domain}/fullchain.pem;
            ssl_certificate_key /etc/letsencrypt/live/{domain}/privkey.pem;

            ssl_protocols TLSv1.2 TLSv1.3;
            ssl_prefer_server_ciphers on;
            ssl_dhparam /etc/ssl/certs/dhparam.pem;
            ssl_ciphers 'ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-SHA384:ECDHE-RSA-AES256-SHA384:ECDHE-ECDSA-AES128-SHA256:ECDHE-RSA-AES128-SHA256';
            ssl_session_timeout 1d;
            ssl_session_cache shared:SSL:50m;
            ssl_stapling on;
            ssl_stapling_verify on;

            location / {{
                proxy_pass http://django_app;
                proxy_http_version 1.1;
                proxy_set_header Upgrade $http_upgrade;
                proxy_set_header Connection $http_upgrade;
                proxy_set_header Host $host;
                proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
                proxy_redirect off;
            }}

            location /ws/ {{
                proxy_pass http://daphne_app;
                proxy_http_version 1.1;
                proxy_set_header Upgrade $http_upgrade;
                proxy_set_header Connection "upgrade";
                proxy_set_header Host $host;
            }}

            location /static/ {{
                alias /app/static/;
            }}

            location /media/ {{
                alias /app/media/;
            }}
        }}
        """

    with open('nginx.conf', 'w') as f:
        f.write(conf)

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python generate_nginx_conf.py <mode> <domain>")
    else:
        mode = sys.argv[1]
        domain = sys.argv[2]
        generate_nginx_conf(mode, domain)
