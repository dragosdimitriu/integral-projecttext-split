#!/bin/bash
# Deploy main branch to production server
# Run this on the production server

echo "=== Deploying Main Branch to Production ==="

APP_DIR="/home/lastchance/ProjectTextApp"
SERVICE_NAME="integral-projecttext"

# Navigate to app directory
cd $APP_DIR || exit 1

# Show current branch
echo ""
echo "Current branch:"
git branch --show-current
echo ""

# Fetch latest changes
echo "Fetching latest changes from remote..."
git fetch origin

# Show what will change
echo ""
echo "Changes to be pulled:"
git log HEAD..origin/main --oneline

# Switch to main branch
echo ""
echo "Switching to main branch..."
git checkout main

# Pull latest changes
echo ""
echo "Pulling latest changes..."
git pull origin main

# Show current commit
echo ""
echo "Current commit:"
git log -1 --oneline

# Check if virtual environment exists
if [ ! -d "$APP_DIR/venv" ]; then
    echo ""
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment and install/update dependencies
echo ""
echo "Installing/updating dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements-prod.txt

# Check if .env file exists
if [ ! -f "$APP_DIR/.env" ]; then
    echo ""
    echo "⚠️  WARNING: .env file not found!"
    echo "Please create .env file with required environment variables."
    echo "See config.example.env for reference."
else
    # Secure .env file permissions (only owner can read/write)
    echo ""
    echo "Securing .env file permissions..."
    chmod 600 $APP_DIR/.env
    echo "✓ .env file permissions set to 600 (owner read/write only)"
fi

# Restart the service
echo ""
echo "Restarting $SERVICE_NAME service..."
sudo systemctl restart $SERVICE_NAME

# Wait a moment for service to start
sleep 2

# Check service status
echo ""
echo "Service status:"
sudo systemctl status $SERVICE_NAME --no-pager | head -15

# Check if service is running
if sudo systemctl is-active --quiet $SERVICE_NAME; then
    echo ""
    echo "✓ Service is running successfully!"
else
    echo ""
    echo "✗ Service failed to start!"
    echo "Check logs with: sudo journalctl -u $SERVICE_NAME -n 50"
    exit 1
fi

# Reload Nginx (in case config changed)
echo ""
echo "Reloading Nginx..."
sudo systemctl reload nginx

# Show recent logs
echo ""
echo "Recent application logs:"
sudo journalctl -u $SERVICE_NAME -n 20 --no-pager

echo ""
echo "=== Deployment Complete ==="
echo ""
echo "Application is now running from main branch"
echo "Check the site: https://pt.schrack.lastchance.ro"

