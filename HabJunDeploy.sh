#!/bin/bash
# deployment-setup.sh - Main setup script for Habla Jungla deployment

# Update system and install dependencies
sudo apt-get update
sudo apt-get upgrade -y
sudo apt-get install -y python3-pip python3-dev nginx supervisor git

# Install Python packages
pip3 install flask flask-cors librosa transformers tensorflow gunicorn

# Create application directory
sudo mkdir -p /var/www/habla-jungla
sudo chown -R $USER:$USER /var/www/habla-jungla

# Create the WSGI entry point
cat > /var/www/habla-jungla/wsgi.py << 'EOL'
from app import app

if __name__ == "__main__":
    app.run()
EOL

# Create the systemd service file
cat > /etc/systemd/system/habla-jungla.service << 'EOL'
[Unit]
Description=Habla Jungla application
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/habla-jungla
Environment="PATH=/var/www/habla-jungla/venv/bin"
ExecStart=/var/www/habla-jungla/venv/bin/gunicorn --workers 3 --bind unix:habla-jungla.sock -m 007 wsgi:app

[Install]
WantedBy=multi-user.target
EOL

# Create Nginx configuration
cat > /etc/nginx/sites-available/habla-jungla << 'EOL'
server {
    listen 80;
    server_name your_domain.com;  # Replace with your domain

    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/habla-jungla/habla-jungla.sock;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # Configure for larger file uploads (audio files)
    client_max_body_size 10M;
    
    # Add security headers
    add_header X-Frame-Options "SAMEORIGIN";
    add_header X-XSS-Protection "1; mode=block";
    add_header X-Content-Type-Options "nosniff";
    
    # Enable CORS
    add_header 'Access-Control-Allow-Origin' '*';
    add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS';
    add_header 'Access-Control-Allow-Headers' 'DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range';
}
EOL

# Create virtual environment setup script
cat > /var/www/habla-jungla/setup_venv.sh << 'EOL'
#!/bin/bash
python3 -m venv venv
source venv/bin/activate
pip install flask flask-cors librosa transformers tensorflow gunicorn
deactivate
EOL

# Create the supervisor configuration
cat > /etc/supervisor/conf.d/habla-jungla.conf << 'EOL'
[program:habla-jungla]
directory=/var/www/habla-jungla
command=/var/www/habla-jungla/venv/bin/gunicorn --workers 3 --bind unix:habla-jungla.sock wsgi:app
autostart=true
autorestart=true
stderr_logfile=/var/log/habla-jungla/habla-jungla.err.log
stdout_logfile=/var/log/habla-jungla/habla-jungla.out.log
user=www-data
group=www-data
environment=PATH="/var/www/habla-jungla/venv/bin"
EOL

# Create the deployment guide
cat > /var/www/habla-jungla/DEPLOYMENT_GUIDE.md << 'EOL'
# Habla Jungla Deployment Guide

## Prerequisites
- Ubuntu 20.04 or newer
- Root access to the server
- Domain name pointing to your server (optional but recommended)

## Step-by-Step Deployment

1. Initial Server Setup
```bash
# Clone the repository
git clone [your-repo-url] /var/www/habla-jungla

# Set up virtual environment
cd /var/www/habla-jungla
chmod +x setup_venv.sh
./setup_venv.sh

# Create log directory
sudo mkdir -p /var/log/habla-jungla
sudo chown -R www-data:www-data /var/log/habla-jungla
```

2. Configure Nginx
```bash
# Enable the site
sudo ln -s /etc/nginx/sites-available/habla-jungla /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx
```

3. Start the Application
```bash
# Start supervisor
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start habla-jungla

# Enable and start the systemd service
sudo systemctl enable habla-jungla
sudo systemctl start habla-jungla
```

4. SSL Configuration (Optional but recommended)
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Obtain SSL certificate
sudo certbot --nginx -d your_domain.com
```

## Maintenance

- View logs:
```bash
sudo tail -f /var/log/habla-jungla/habla-jungla.out.log
sudo tail -f /var/log/habla-jungla/habla-jungla.err.log
```

- Restart application:
```bash
sudo systemctl restart habla-jungla
# or
sudo supervisorctl restart habla-jungla
```

- Update application:
```bash
cd /var/www/habla-jungla
git pull
sudo supervisorctl restart habla-jungla
```

## Troubleshooting

1. Check application status:
```bash
sudo systemctl status habla-jungla
sudo supervisorctl status habla-jungla
```

2. Check Nginx status:
```bash
sudo nginx -t
sudo systemctl status nginx
```

3. Common issues:
- Port 80 already in use: Check other Nginx configurations
- Socket file permission issues: Verify www-data ownership
- Python package issues: Check venv activation and requirements

## Security Considerations

1. Firewall setup:
```bash
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

2. Regular updates:
```bash
sudo apt update
sudo apt upgrade
```

3. Monitor logs for suspicious activity
4. Keep Python packages updated
5. Regular backup of application data
EOL

# Make scripts executable
chmod +x /var/www/habla-jungla/setup_venv.sh

# Create necessary symbolic links
sudo ln -s /etc/nginx/sites-available/habla-jungla /etc/nginx/sites-enabled

# Set proper permissions
sudo chown -R www-data:www-data /var/www/habla-jungla
sudo chmod -R 755 /var/www/habla-jungla

# Restart services
sudo systemctl daemon-reload
sudo systemctl restart nginx
sudo supervisorctl reread
sudo supervisorctl update

echo "Deployment setup complete! Please follow the instructions in DEPLOYMENT_GUIDE.md"
