#!/bin/bash
# Comprehensive server diagnosis script
# Run this on the server to check what's wrong

echo "=== Server Diagnosis ==="
echo ""

# Check Gunicorn service status
echo "1. Checking Gunicorn service..."
sudo systemctl status integral-projecttext --no-pager -l | head -20
echo ""

# Check recent Gunicorn logs
echo "2. Recent Gunicorn logs (last 30 lines):"
sudo journalctl -u integral-projecttext -n 30 --no-pager
echo ""

# Check Nginx status
echo "3. Checking Nginx status..."
sudo systemctl status nginx --no-pager | head -15
echo ""

# Check Nginx error logs
echo "4. Recent Nginx error logs:"
sudo tail -20 /var/log/nginx/error.log
echo ""

# Check Nginx access logs
echo "5. Recent Nginx access logs:"
sudo tail -10 /var/log/nginx/access.log
echo ""

# Test Nginx configuration
echo "6. Testing Nginx configuration..."
sudo nginx -t
echo ""

# Check if static directory exists
echo "7. Checking static directory:"
if [ -d "/home/lastchance/ProjectTextApp/static" ]; then
    echo "✓ Static directory exists"
    ls -la /home/lastchance/ProjectTextApp/static/
    echo ""
    if [ -d "/home/lastchance/ProjectTextApp/static/css" ]; then
        echo "✓ CSS directory exists"
        ls -la /home/lastchance/ProjectTextApp/static/css/
    else
        echo "✗ CSS directory missing!"
    fi
else
    echo "✗ Static directory does not exist!"
fi
echo ""

# Check if app is listening on port 5000
echo "8. Checking if app is listening on port 5000:"
sudo netstat -tlnp | grep 5000 || echo "Nothing listening on port 5000"
echo ""

# Check current Nginx config
echo "9. Current Nginx configuration:"
sudo cat /etc/nginx/sites-available/integral-projecttext
echo ""

# Check Flask app file
echo "10. Checking if app.py exists:"
if [ -f "/home/lastchance/ProjectTextApp/app.py" ]; then
    echo "✓ app.py exists"
else
    echo "✗ app.py missing!"
fi

echo ""
echo "=== Diagnosis Complete ==="

