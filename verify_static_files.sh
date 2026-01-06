#!/bin/bash
# Verify static files are accessible and properly configured

echo "=== Verifying Static Files Configuration ==="

STATIC_DIR="/home/lastchance/ProjectTextApp/static"

echo "1. Checking static directory structure..."
if [ -d "$STATIC_DIR" ]; then
    echo "✓ Static directory exists"
    tree -L 3 $STATIC_DIR 2>/dev/null || find $STATIC_DIR -type f | head -20
else
    echo "✗ Static directory does not exist!"
    exit 1
fi

echo ""
echo "2. Checking critical files..."
CRITICAL_FILES=(
    "$STATIC_DIR/css/style.css"
    "$STATIC_DIR/images/logo.png"
    "$STATIC_DIR/images/icon.png"
    "$STATIC_DIR/images/default-avatar.svg"
)

for file in "${CRITICAL_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "✓ $(basename $file) exists"
        ls -lh "$file"
    else
        echo "✗ $(basename $file) NOT FOUND at $file"
    fi
done

echo ""
echo "3. Testing Nginx configuration..."
sudo nginx -t

echo ""
echo "4. Checking Nginx static location..."
grep -A 5 "location /static" /etc/nginx/sites-available/integral-projecttext || echo "Static location not found in config"

echo ""
echo "5. Testing file access as www-data..."
if sudo -u www-data test -r "$STATIC_DIR/css/style.css"; then
    echo "✓ www-data can read style.css"
    echo "File content preview (first 3 lines):"
    sudo -u www-data head -3 "$STATIC_DIR/css/style.css"
else
    echo "✗ www-data CANNOT read style.css"
    echo "This is the problem! Fixing permissions..."
    sudo chmod 644 "$STATIC_DIR/css/style.css"
    sudo chmod 755 "$STATIC_DIR/css"
    sudo chmod 755 "$STATIC_DIR"
fi

echo ""
echo "6. Checking directory permissions path..."
echo "Checking: /home"
ls -ld /home
echo "Checking: /home/lastchance"
ls -ld /home/lastchance
echo "Checking: /home/lastchance/ProjectTextApp"
ls -ld /home/lastchance/ProjectTextApp
echo "Checking: $STATIC_DIR"
ls -ld $STATIC_DIR

echo ""
echo "=== Verification Complete ==="

