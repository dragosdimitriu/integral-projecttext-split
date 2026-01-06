#!/bin/bash
# Diagnostic script for integral-projecttext service
# Run this on the server to diagnose issues

echo "=== Integral ProjectText Service Diagnostics ==="
echo ""

echo "1. Checking service status..."
sudo systemctl status integral-projecttext --no-pager -l
echo ""

echo "2. Checking recent service logs..."
sudo journalctl -u integral-projecttext -n 30 --no-pager
echo ""

echo "3. Checking if .env file exists..."
if [ -f "/home/lastchance/ProjectTextApp/.env" ]; then
    echo "✓ .env file exists"
    echo "Checking required variables..."
    source /home/lastchance/ProjectTextApp/.env
    if [ -z "$SECRET_KEY" ]; then
        echo "✗ SECRET_KEY is not set"
    else
        echo "✓ SECRET_KEY is set"
    fi
    if [ -z "$GOOGLE_CLIENT_ID" ]; then
        echo "✗ GOOGLE_CLIENT_ID is not set"
    else
        echo "✓ GOOGLE_CLIENT_ID is set"
    fi
    if [ -z "$GOOGLE_CLIENT_SECRET" ]; then
        echo "✗ GOOGLE_CLIENT_SECRET is not set"
    else
        echo "✓ GOOGLE_CLIENT_SECRET is set"
    fi
else
    echo "✗ .env file does not exist!"
fi
echo ""

echo "4. Checking virtual environment..."
if [ -d "/home/lastchance/ProjectTextApp/venv" ]; then
    echo "✓ Virtual environment exists"
    if [ -f "/home/lastchance/ProjectTextApp/venv/bin/python" ]; then
        echo "✓ Python executable exists"
        /home/lastchance/ProjectTextApp/venv/bin/python --version
    else
        echo "✗ Python executable not found in venv"
    fi
    if [ -f "/home/lastchance/ProjectTextApp/venv/bin/gunicorn" ]; then
        echo "✓ Gunicorn executable exists"
    else
        echo "✗ Gunicorn not found - needs installation"
    fi
else
    echo "✗ Virtual environment does not exist!"
fi
echo ""

echo "5. Checking Python imports..."
cd /home/lastchance/ProjectTextApp
source venv/bin/activate 2>/dev/null
if [ $? -eq 0 ]; then
    echo "Testing imports..."
    python -c "import flask; print('✓ Flask')" 2>&1
    python -c "import openpyxl; print('✓ openpyxl')" 2>&1
    python -c "import flask_login; print('✓ flask_login')" 2>&1
    python -c "import authlib; print('✓ authlib')" 2>&1
    python -c "from dotenv import load_dotenv; print('✓ python-dotenv')" 2>&1
    python -c "import split; print('✓ split module')" 2>&1
    python -c "from app import app; print('✓ app module')" 2>&1
else
    echo "✗ Failed to activate virtual environment"
fi
echo ""

echo "6. Checking file permissions..."
ls -la /home/lastchance/ProjectTextApp/ | head -5
echo ""

echo "7. Testing gunicorn manually..."
cd /home/lastchance/ProjectTextApp
source venv/bin/activate 2>/dev/null
if [ -f ".env" ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi
timeout 5 gunicorn --config gunicorn_config.py wsgi:app 2>&1 || echo "Gunicorn test completed (timeout expected)"
echo ""

echo "=== Diagnostics Complete ==="
echo ""
echo "Common fixes:"
echo "1. Install dependencies: cd /home/lastchance/ProjectTextApp && source venv/bin/activate && pip install -r requirements-prod.txt"
echo "2. Create .env file with required variables"
echo "3. Check logs: sudo journalctl -u integral-projecttext -f"

