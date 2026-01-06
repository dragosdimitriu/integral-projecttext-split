#!/bin/bash
# Setup HTTPS for Integral ProjectText
# This script configures Nginx with SSL certificates

echo "=== Setting Up HTTPS Configuration ==="

# Check if Certbot is installed
if ! command -v certbot &> /dev/null; then
    echo "Installing Certbot..."
    sudo apt-get update
    sudo apt-get install -y certbot python3-certbot-nginx
fi

# Backup current config
if [ -f "/etc/nginx/sites-available/integral-projecttext" ]; then
    echo "Backing up current Nginx configuration..."
    sudo cp /etc/nginx/sites-available/integral-projecttext /etc/nginx/sites-available/integral-projecttext.backup.$(date +%Y%m%d_%H%M%S)
fi

# Create HTTPS-ready Nginx config (before SSL certificates)
echo "Creating HTTPS-ready Nginx configuration..."
sudo tee /etc/nginx/sites-available/integral-projecttext > /dev/null << 'NGINXEOF'
# HTTP server - redirect to HTTPS
server {
    listen 80;
    listen [::]:80;
    server_name pt.schrack.lastchance.ro 185.125.109.150;

    # Allow Let's Encrypt verification
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }

    # Redirect all other HTTP requests to HTTPS
    location / {
        return 301 https://$server_name$request_uri;
    }
}

# HTTPS server (will be updated by Certbot)
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name pt.schrack.lastchance.ro 185.125.109.150;

    # SSL Certificate paths (Certbot will update these)
    # ssl_certificate /etc/letsencrypt/live/pt.schrack.lastchance.ro/fullchain.pem;
    # ssl_certificate_key /etc/letsencrypt/live/pt.schrack.lastchance.ro/privkey.pem;
    
    # Include SSL configuration snippet (will be created by Certbot)
    # include /etc/letsencrypt/options-ssl-nginx.conf;
    # ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # File upload size limit
    client_max_body_size 16M;

    # Flask serves static files from /static (no trailing slash)
    location /static {
        alias /home/lastchance/ProjectTextApp/static;
        expires 30d;
        add_header Cache-Control "public";
        access_log off;
    }

    # Proxy all other requests to Flask/Gunicorn
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-Port $server_port;
        proxy_redirect off;
        
        # WebSocket support (if needed in future)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
NGINXEOF

# Test Nginx configuration
echo ""
echo "Testing Nginx configuration..."
sudo nginx -t

if [ $? -ne 0 ]; then
    echo "✗ Nginx configuration has errors!"
    echo "Restoring backup..."
    if [ -f "/etc/nginx/sites-available/integral-projecttext.backup.$(date +%Y%m%d_%H%M%S)" ]; then
        sudo cp /etc/nginx/sites-available/integral-projecttext.backup.* /etc/nginx/sites-available/integral-projecttext
    fi
    exit 1
fi

# Reload Nginx
echo "Reloading Nginx..."
sudo systemctl reload nginx

# Obtain SSL certificate
echo ""
echo "=== Obtaining SSL Certificate ==="
echo "This will prompt you for email and agreement to terms."
echo "Press Enter to continue or Ctrl+C to cancel..."
read

sudo certbot --nginx -d pt.schrack.lastchance.ro --non-interactive --agree-tos --email admin@lastchance.ro --redirect

if [ $? -eq 0 ]; then
    echo ""
    echo "✓ SSL certificate obtained successfully!"
    echo ""
    echo "=== Setup Complete ==="
    echo ""
    echo "Your site is now available at: https://pt.schrack.lastchance.ro"
    echo ""
    echo "Next steps:"
    echo "1. Update Google OAuth redirect URI to: https://pt.schrack.lastchance.ro/callback"
    echo "2. Set SESSION_COOKIE_SECURE=True in /home/lastchance/ProjectTextApp/.env"
    echo "3. Restart the service: sudo systemctl restart integral-projecttext"
    echo ""
    echo "SSL certificate will auto-renew via Certbot."
else
    echo ""
    echo "✗ SSL certificate setup failed!"
    echo "You can try manually: sudo certbot --nginx -d pt.schrack.lastchance.ro"
    exit 1
fi

