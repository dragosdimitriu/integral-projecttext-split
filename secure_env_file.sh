#!/bin/bash
# Secure .env file permissions
# Run this on the production server

APP_DIR="/home/lastchance/ProjectTextApp"
ENV_FILE="$APP_DIR/.env"

echo "=== Securing .env File ==="

if [ ! -f "$ENV_FILE" ]; then
    echo "✗ .env file not found at $ENV_FILE"
    exit 1
fi

# Show current permissions
echo ""
echo "Current permissions:"
ls -lh $ENV_FILE

# Fix permissions (owner read/write only)
echo ""
echo "Setting secure permissions (600 = owner read/write only)..."
chmod 600 $ENV_FILE

# Verify permissions
echo ""
echo "New permissions:"
ls -lh $ENV_FILE

# Check if correct
PERMS=$(stat -c "%a" $ENV_FILE)
if [ "$PERMS" = "600" ]; then
    echo ""
    echo "✓ .env file is now secure (600)"
    echo "Only the owner (lastchance) can read/write this file"
else
    echo ""
    echo "✗ Failed to set permissions correctly"
    exit 1
fi

# Also check parent directory
echo ""
echo "Checking parent directory permissions..."
PARENT_PERMS=$(stat -c "%a" $APP_DIR)
if [ "$PARENT_PERMS" != "755" ] && [ "$PARENT_PERMS" != "750" ]; then
    echo "⚠️  Warning: Parent directory permissions are $PARENT_PERMS"
    echo "Recommended: 755 or 750"
fi

echo ""
echo "=== Security Check Complete ==="
echo ""
echo "Best practices:"
echo "✓ .env file permissions: 600 (owner read/write only)"
echo "✓ .env file is in .gitignore (not tracked by git)"
echo "✓ Use config.example.env as a template (without secrets)"
echo "✓ Never commit .env file to git"
echo "✓ Rotate secrets periodically"

