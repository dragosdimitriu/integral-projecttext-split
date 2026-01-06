#!/bin/bash
# Production Server Setup Script
# Run this script on the production server as root

set -e

echo "=== Integral ProjectText FileProcessor - Production Setup ==="

# Update system
echo "Updating system packages..."
apt update && apt upgrade -y

# Install required packages
echo "Installing required packages..."
apt install -y python3 python3-pip python3-venv git nginx supervisor certbot python3-certbot-nginx ufw

# Ensure lastchance user exists (should already exist)
echo "Checking lastchance user..."
if ! id -u lastchance > /dev/null 2>&1; then
    echo "ERROR: lastchance user does not exist. Please create it first."
    exit 1
fi

# Set up firewall
echo "Configuring firewall..."
ufw --force enable
ufw allow 2324/tcp  # SSH on custom port
ufw allow 'Nginx Full'

# Switch to lastchance user for application setup
echo "Setting up application..."
su - lastchance << 'EOF'
cd /home/lastchance

# Clone repository
if [ ! -d "ProjectTextApp" ]; then
    git clone https://github.com/dragosdimitriu/integral-projecttext-split.git ProjectTextApp
fi

cd ProjectTextApp
git fetch origin
git checkout authentication

# Create virtual environment
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate
pip install --upgrade pip
pip install -r requirements-prod.txt

# Create directories
mkdir -p uploads outputs
chmod 755 uploads outputs

# Generate secret key if .env doesn't exist
if [ ! -f ".env" ]; then
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
    cat > .env << ENVEOF
SECRET_KEY=$SECRET_KEY
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
SESSION_COOKIE_SECURE=True
FLASK_DEBUG=False
ENVEOF
    echo ".env file created. Please update GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET"
fi

EOF

# Create Gunicorn config
echo "Creating Gunicorn configuration..."
cat > /home/lastchance/ProjectTextApp/gunicorn_config.py << 'GUNICORNEOF'
bind = "127.0.0.1:5000"
workers = 4
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2
max_requests = 1000
max_requests_jitter = 100
preload_app = True
GUNICORNEOF

chown lastchance:lastchance /home/lastchance/ProjectTextApp/gunicorn_config.py

# Create systemd service
echo "Creating systemd service..."
cat > /etc/systemd/system/integral-projecttext.service << 'SERVICEEOF'
[Unit]
Description=Integral ProjectText FileProcessor Gunicorn daemon
After=network.target

[Service]
User=lastchance
Group=lastchance
WorkingDirectory=/home/lastchance/ProjectTextApp
Environment="PATH=/home/lastchance/ProjectTextApp/venv/bin"
EnvironmentFile=/home/lastchance/ProjectTextApp/.env
ExecStart=/home/lastchance/ProjectTextApp/venv/bin/gunicorn --config /home/lastchance/ProjectTextApp/gunicorn_config.py wsgi:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
SERVICEEOF

# Create Nginx config
echo "Creating Nginx configuration..."
cat > /etc/nginx/sites-available/integral-projecttext << 'NGINXEOF'
server {
    listen 80;
    server_name pt.schrack.lastchance.ro 185.125.109.150;

    client_max_body_size 16M;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }

    location /static {
        alias /home/lastchance/ProjectTextApp/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
NGINXEOF

# Enable Nginx site
ln -sf /etc/nginx/sites-available/integral-projecttext /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Set permissions
chown -R lastchance:lastchance /home/lastchance/ProjectTextApp

# Reload systemd and start services
echo "Starting services..."
systemctl daemon-reload
systemctl enable integral-projecttext
systemctl restart integral-projecttext
systemctl restart nginx

echo ""
echo "=== Setup Complete ==="
echo ""
echo "Next steps:"
echo "1. Edit /home/lastchance/ProjectTextApp/.env and add your Google OAuth credentials"
echo "2. Restart the service: sudo systemctl restart integral-projecttext"
echo "3. Set up SSL: sudo certbot --nginx -d pt.schrack.lastchance.ro"
echo "4. Update Google OAuth redirect URI to: https://pt.schrack.lastchance.ro/callback"
echo ""
echo "Check service status: sudo systemctl status integral-projecttext"
echo "View logs: sudo journalctl -u integral-projecttext -f"

