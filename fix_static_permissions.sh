#!/bin/bash
# Fix static file permissions for Nginx
# This script fixes 403 Forbidden errors for static files

echo "=== Fixing Static File Permissions ==="

STATIC_DIR="/home/lastchance/ProjectTextApp/static"
NGINX_USER="www-data"

# Check if static directory exists
if [ ! -d "$STATIC_DIR" ]; then
    echo "✗ Static directory does not exist: $STATIC_DIR"
    exit 1
fi

echo "1. Checking current permissions..."
ls -la $STATIC_DIR
echo ""

# Fix directory ownership
echo "2. Setting directory ownership..."
sudo chown -R lastchance:lastchance $STATIC_DIR
echo "✓ Ownership set to lastchance:lastchance"
echo ""

# Fix directory permissions (readable and executable by all)
echo "3. Setting directory permissions..."
find $STATIC_DIR -type d -exec sudo chmod 755 {} \;
echo "✓ Directories set to 755"
echo ""

# Fix file permissions (readable by all)
echo "4. Setting file permissions..."
find $STATIC_DIR -type f -exec sudo chmod 644 {} \;
echo "✓ Files set to 644"
echo ""

# Verify permissions
echo "5. Verifying permissions..."
ls -la $STATIC_DIR
echo ""
ls -la $STATIC_DIR/css/ 2>/dev/null || echo "CSS directory not found"
ls -la $STATIC_DIR/images/ 2>/dev/null || echo "Images directory not found"
echo ""

# Check if Nginx can access (test as www-data user)
echo "6. Testing Nginx access..."
if sudo -u $NGINX_USER test -r $STATIC_DIR; then
    echo "✓ Nginx can read static directory"
else
    echo "✗ Nginx cannot read static directory"
    echo "Making directory world-readable..."
    sudo chmod 755 $STATIC_DIR
    sudo chmod 755 $(dirname $STATIC_DIR)
fi

# Check parent directory permissions
echo ""
echo "7. Checking parent directory permissions..."
PARENT_DIR=$(dirname $STATIC_DIR)
echo "Parent directory: $PARENT_DIR"
ls -ld $PARENT_DIR
if [ ! -x "$PARENT_DIR" ]; then
    echo "Making parent directory executable..."
    sudo chmod 755 $PARENT_DIR
fi

# Verify specific files exist
echo ""
echo "8. Verifying critical files exist..."
if [ -f "$STATIC_DIR/css/style.css" ]; then
    echo "✓ style.css exists"
    ls -l $STATIC_DIR/css/style.css
else
    echo "✗ style.css NOT FOUND at $STATIC_DIR/css/style.css"
fi

if [ -d "$STATIC_DIR/images" ]; then
    echo "✓ images directory exists"
    ls -la $STATIC_DIR/images/ | head -5
else
    echo "✗ images directory NOT FOUND"
fi

echo ""
echo "=== Permission Fix Complete ==="
echo ""
echo "If issues persist, check:"
echo "1. SELinux status: getenforce (if enabled, may need to set context)"
echo "2. Nginx error log: sudo tail -f /var/log/nginx/error.log"
echo "3. Test file access: sudo -u www-data cat $STATIC_DIR/css/style.css"

