# cloud computing assignments

Build1 - Checking the APIs on an assumed schema of the table. Multivalued attributes not included

### adding a reverse proxy setup:
install nginx, and stop apache2 if its running.
add the following file as ```/etc/nginx/sites-available/reverse-proxy.conf``` :
```server {
    listen 80;
    location / {
        proxy_pass http://0.0.0.0:8080;
    }
}```

create a symbolic link:

```ln -s /etc/nginx/sites-available/reverse-proxy.conf /etc/nginx/sites-enabled/reverse-proxy.conf```

disable default virtual host:
```unlink /etc/nginx/sites-enabled/default```

restart nginx:
```sudo systemctl restart nginx```