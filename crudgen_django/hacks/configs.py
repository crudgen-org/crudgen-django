NGINX_CONF_TEMPLATE = """# nginx.default

server {
    listen 8020;
    server_name {{server_name}};

    location / {
        proxy_pass http://127.0.0.1:8010;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
    location /static {
        root /opt/app/{{project_name}};
    }
}"""

START_SERVER_CMD_TEMPLATE = """#!/usr/bin/env bash
# start-server.sh
if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ] ; then
    (cd {{app_name}}; python manage.py createsuperuser --no-input)
fi
python {{project_name}}/manage.py migrate
(cd {{project_name}}; gunicorn {{project_name}}.wsgi --user www-data --bind 0.0.0.0:8010 --workers 1) &
nginx -g "daemon off;"
"""

DockerFile_TEMPLATE = """# Dockerfile

FROM python:3.7-buster

# install nginx
RUN apt-get update && apt-get install nginx -y --no-install-recommends
COPY nginx.default /etc/nginx/sites-available/default
RUN ln -sf /dev/stdout /var/log/nginx/access.log \
    && ln -sf /dev/stderr /var/log/nginx/error.log

# copy source and install dependencies
RUN mkdir -p /opt/app
RUN mkdir -p /opt/app/pip_cache
RUN mkdir -p /opt/app/{{project_name}}
COPY requirements.txt start-server.sh /opt/app/
RUN chmod 755 /opt/app/start-server.sh
COPY {{project_name}} /opt/app/{{project_name}}/
WORKDIR /opt/app
RUN pip install -r requirements.txt --cache-dir /opt/app/pip_cache
RUN python {{project_name}}/manage.py collectstatic
RUN chown -R www-data:www-data /opt/app

# start server
EXPOSE 8020
STOPSIGNAL SIGTERM
CMD ["/opt/app/start-server.sh"]"""