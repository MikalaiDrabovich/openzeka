#!/usr/bin/env bash
# This script will install NGINX and make configuration to access your web server with http://localhost
sudo apt-get install -y nginx
# sudo /etc/init.d/nginx start
# Backup existing default site configuration file to default-backup
# sudo mv /etc/nginx/sites-enabled/default /etc/nginx/sites-enabled/default-backup
sudo rm /etc/nginx/sites-enabled/default
# Create openzeka site configuration file
sudo touch /etc/nginx/sites-available/openzeka
sudo ln -s /etc/nginx/sites-available/openzeka /etc/nginx/sites-enabled/openzeka
# Edit openzeka configuration file. All http://localhost request redirect the python server
echo "
server {
    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }
    location /static {
        alias  $(pwd)/app/static/;
    }
}" | sudo tee -a /etc/nginx/sites-available/openzeka
# Retsart server
sudo /etc/init.d/nginx restart