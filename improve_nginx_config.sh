#!/bin/bash
# Improve existing Nginx HTTPS configuration
# Adds security headers, http2, IPv6, and optimizations

echo "=== Improving Nginx HTTPS Configuration ==="

# Backup current config
if [ -f "/etc/nginx/sites-available/integral-projecttext" ]; then
    echo "Backing up current configuration..."
    sudo cp /etc/nginx/sites-available/integral-projecttext /etc/nginx/sites-available/integral-projecttext.backup.$(date +%Y%m%d_%H%M%S)
fi

# Create improved configuration
echo "Creating improved configuration..."
sudo tee /etc/nginx/sites-available/integral-projecttext > /dev/null << 'NGINXEOF'
# HTTP server - redirect to HTTPS
server {
    listen 80;
    listen [::]:80;
    server_name pt.schrack.lastchance.ro 185.125.109.150;

    # Redirect all HTTP requests to HTTPS
    return 301 https://$server_name$request_uri;
}

# HTTPS server
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name pt.schrack.lastchance.ro 185.125.109.150;

    # SSL Certificates (managed by Certbot)
    ssl_certificate /etc/letsencrypt/live/pt.schrack.lastchance.ro/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/pt.schrack.lastchance.ro/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

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
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
NGINXEOF

# Test Nginx configuration
echo ""
echo "Testing Nginx configuration..."
sudo nginx -t

if [ $? -eq 0 ]; then
    echo "✓ Nginx configuration is valid"
    echo "Reloading Nginx..."
    sudo systemctl reload nginx
    echo "✓ Nginx reloaded successfully"
    echo ""
    echo "=== Improvements Applied ==="
    echo "✓ Added HTTP/2 support"
    echo "✓ Added IPv6 support"
    echo "✓ Added security headers (HSTS, X-Frame-Options, etc.)"
    echo "✓ Improved proxy headers"
    echo "✓ Added timeouts for better reliability"
    echo "✓ Cleaner HTTP redirect"
else
    echo "✗ Nginx configuration has errors!"
    echo "Restoring backup..."
    sudo cp /etc/nginx/sites-available/integral-projecttext.backup.* /etc/nginx/sites-available/integral-projecttext 2>/dev/null || echo "No backup found"
    exit 1
fi

echo ""
echo "Configuration is now optimized for production!"

