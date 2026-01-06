# Troubleshooting Guide

## Service Won't Start

### Check Service Logs

```bash
sudo journalctl -u integral-projecttext -n 50 --no-pager
```

Or follow logs in real-time:
```bash
sudo journalctl -u integral-projecttext -f
```

### Common Issues and Solutions

#### 1. Python/Module Import Errors

**Symptoms**: `ModuleNotFoundError` or `ImportError` in logs

**Solution**:
```bash
cd /home/lastchance/ProjectTextApp
source venv/bin/activate
pip install -r requirements-prod.txt
```

#### 2. Missing .env File

**Symptoms**: `KeyError` or environment variable errors

**Solution**:
```bash
cd /home/lastchance/ProjectTextApp
nano .env
```

Ensure it contains:
```env
SECRET_KEY=your-secret-key-here
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
SESSION_COOKIE_SECURE=True
FLASK_DEBUG=False
```

#### 3. Permission Issues

**Symptoms**: Permission denied errors

**Solution**:
```bash
sudo chown -R lastchance:lastchance /home/lastchance/ProjectTextApp
chmod +x /home/lastchance/ProjectTextApp/venv/bin/gunicorn
```

#### 4. Port Already in Use

**Symptoms**: `Address already in use` error

**Solution**:
```bash
sudo netstat -tulpn | grep 5000
# Kill the process if needed
sudo kill -9 <PID>
sudo systemctl restart integral-projecttext
```

#### 5. Invalid Python Path

**Symptoms**: `python: command not found` or path errors

**Solution**:
```bash
# Verify virtual environment exists
ls -la /home/lastchance/ProjectTextApp/venv/bin/

# Recreate if needed
cd /home/lastchance/ProjectTextApp
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-prod.txt
```

#### 6. Gunicorn Config Issues

**Symptoms**: Config file errors

**Solution**:
```bash
# Test gunicorn config manually
cd /home/lastchance/ProjectTextApp
source venv/bin/activate
gunicorn --config gunicorn_config.py wsgi:app
```

#### 7. Missing Dependencies

**Symptoms**: Import errors for specific modules

**Solution**:
```bash
cd /home/lastchance/ProjectTextApp
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements-prod.txt
```

### Manual Service Test

Test the service manually to see exact error:

```bash
cd /home/lastchance/ProjectTextApp
source venv/bin/activate
export $(cat .env | xargs)
python wsgi.py
```

Or test with gunicorn directly:
```bash
cd /home/lastchance/ProjectTextApp
source venv/bin/activate
export $(cat .env | xargs)
gunicorn --config gunicorn_config.py wsgi:app
```

### Check Service Configuration

Verify service file is correct:
```bash
sudo cat /etc/systemd/system/integral-projecttext.service
```

### Restart Service After Fixes

```bash
sudo systemctl daemon-reload
sudo systemctl restart integral-projecttext
sudo systemctl status integral-projecttext
```

