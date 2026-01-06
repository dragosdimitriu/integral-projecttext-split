#!/bin/bash
# Fix Nginx static file serving
# Run this on the server

echo "=== Fixing Nginx Static File Configuration ==="

# Backup current config
sudo cp /etc/nginx/sites-available/integral-projecttext /etc/nginx/sites-available/integral-projecttext.backup

# Update Nginx config
sudo tee /etc/nginx/sites-available/integral-projecttext > /dev/null << 'NGINXEOF'
server {
    listen 80;
    server_name pt.schrack.lastchance.ro 185.125.109.150;

    client_max_body_size 16M;

    location /static/ {
        alias /home/lastchance/ProjectTextApp/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
        access_log off;
    }

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }
}
NGINXEOF

# Test Nginx configuration
echo "Testing Nginx configuration..."
sudo nginx -t

if [ $? -eq 0 ]; then
    echo "✓ Nginx configuration is valid"
    echo "Reloading Nginx..."
    sudo systemctl reload nginx
    echo "✓ Nginx reloaded"
else
    echo "✗ Nginx configuration has errors!"
    echo "Restoring backup..."
    sudo cp /etc/nginx/sites-available/integral-projecttext.backup /etc/nginx/sites-available/integral-projecttext
    exit 1
fi

# Check static directory permissions
echo ""
echo "Checking static directory..."
if [ -d "/home/lastchance/ProjectTextApp/static" ]; then
    echo "✓ Static directory exists"
    ls -la /home/lastchance/ProjectTextApp/static/
    echo ""
    echo "Setting permissions..."
    sudo chown -R lastchance:lastchance /home/lastchance/ProjectTextApp/static
    sudo chmod -R 755 /home/lastchance/ProjectTextApp/static
    echo "✓ Permissions set"
else
    echo "✗ Static directory does not exist!"
fi

echo ""
echo "=== Fix Complete ==="
echo ""
echo "Test the site and check browser console (F12) for any remaining CSS errors"

