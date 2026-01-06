#!/bin/bash
# Emergency fix - restore working Nginx configuration
# Run this if the site is completely broken

echo "=== Emergency Nginx Fix ==="

# Restore backup if it exists
if [ -f "/etc/nginx/sites-available/integral-projecttext.backup" ]; then
    echo "Restoring backup configuration..."
    sudo cp /etc/nginx/sites-available/integral-projecttext.backup /etc/nginx/sites-available/integral-projecttext
    sudo nginx -t
    if [ $? -eq 0 ]; then
        sudo systemctl reload nginx
        echo "✓ Backup restored and Nginx reloaded"
    else
        echo "✗ Backup also has errors!"
    fi
fi

# Create a simple working configuration (HTTP only - for emergency)
echo ""
echo "Creating simple working configuration (HTTP only)..."
echo "NOTE: This is HTTP only. Run setup_https.sh after fixing to enable HTTPS."
sudo tee /etc/nginx/sites-available/integral-projecttext > /dev/null << 'NGINXEOF'
server {
    listen 80;
    listen [::]:80;
    server_name pt.schrack.lastchance.ro 185.125.109.150;

    client_max_body_size 16M;

    # Flask serves static files from /static (no trailing slash)
    location /static {
        alias /home/lastchance/ProjectTextApp/static;
        expires 30d;
        add_header Cache-Control "public";
    }

    # Proxy everything else to Flask
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-Port $server_port;
    }
}
NGINXEOF

# Test configuration
echo "Testing Nginx configuration..."
sudo nginx -t

if [ $? -eq 0 ]; then
    echo "✓ Configuration is valid"
    echo "Reloading Nginx..."
    sudo systemctl reload nginx
    echo "✓ Nginx reloaded"
    
    # Check Gunicorn
    echo ""
    echo "Checking Gunicorn service..."
    sudo systemctl status integral-projecttext --no-pager | head -10
    
    if ! sudo systemctl is-active --quiet integral-projecttext; then
        echo ""
        echo "Gunicorn is not running. Starting it..."
        sudo systemctl start integral-projecttext
        sleep 2
        sudo systemctl status integral-projecttext --no-pager | head -10
    fi
else
    echo "✗ Configuration has errors!"
    exit 1
fi

echo ""
echo "=== Fix Complete ==="
echo "Check the site now: https://pt.schrack.lastchance.ro/"

