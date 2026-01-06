# Production Deployment Guide

This guide explains how to deploy the Integral ProjectText FileProcessor to production.

## Production WSGI Servers

Flask's built-in development server is **NOT** suitable for production. Use one of these production-ready servers:

### Option 1: Gunicorn (Linux/Mac)

1. Install Gunicorn:
```bash
pip install gunicorn
```

2. Run the application:
```bash
gunicorn -w 4 -b 0.0.0.0:5000 wsgi:app
```

Options:
- `-w 4`: Number of worker processes (adjust based on CPU cores)
- `-b 0.0.0.0:5000`: Bind to all interfaces on port 5000
- `wsgi:app`: Module and application instance

### Option 2: Waitress (Cross-platform - Windows/Linux/Mac)

1. Install Waitress:
```bash
pip install waitress
```

2. Run the application:
```bash
waitress-serve --host=0.0.0.0 --port=5000 wsgi:app
```

### Option 3: uWSGI (Advanced)

```bash
pip install uwsgi
uwsgi --http :5000 --module wsgi:app --processes 4 --threads 2
```

## Production Configuration

### 1. Environment Variables

Set these in your production environment:

```bash
# Required
SECRET_KEY=your-strong-secret-key-here
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret

# Optional - Session Security
SESSION_COOKIE_SECURE=True  # Requires HTTPS
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE=Lax
```

### 2. Update app.py for Production

Make sure these settings are configured:

```python
app.config['SESSION_COOKIE_SECURE'] = True  # Enable for HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
```

### 3. HTTPS Setup

**Required for OAuth in production!**

- Use a reverse proxy (Nginx, Apache) with SSL certificates
- Or use a platform that provides HTTPS (Heroku, AWS, Azure, etc.)

## Deployment Platforms

### Heroku

1. Create `Procfile`:
```
web: gunicorn wsgi:app
```

2. Deploy:
```bash
heroku create your-app-name
git push heroku main
heroku config:set SECRET_KEY=your-secret-key
heroku config:set GOOGLE_CLIENT_ID=your-client-id
heroku config:set GOOGLE_CLIENT_SECRET=your-secret
```

### Docker

Create `Dockerfile`:
```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "wsgi:app"]
```

Build and run:
```bash
docker build -t projecttext-processor .
docker run -p 5000:5000 -e SECRET_KEY=your-key -e GOOGLE_CLIENT_ID=... -e GOOGLE_CLIENT_SECRET=... projecttext-processor
```

### Windows Server (IIS)

Use Waitress with IIS:
1. Install Waitress
2. Configure IIS as reverse proxy
3. Run Waitress as Windows Service

### Linux (systemd Service)

Create `/etc/systemd/system/projecttext.service`:
```ini
[Unit]
Description=Integral ProjectText FileProcessor
After=network.target

[Service]
User=www-data
WorkingDirectory=/path/to/app
Environment="SECRET_KEY=your-secret-key"
Environment="GOOGLE_CLIENT_ID=your-client-id"
Environment="GOOGLE_CLIENT_SECRET=your-secret"
ExecStart=/usr/bin/gunicorn -w 4 -b 127.0.0.1:5000 wsgi:app
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable projecttext
sudo systemctl start projecttext
```

## Nginx Reverse Proxy Example

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Security Checklist

- [ ] Use HTTPS (required for OAuth)
- [ ] Set strong SECRET_KEY
- [ ] Configure SESSION_COOKIE_SECURE=True
- [ ] Use production WSGI server (Gunicorn/Waitress)
- [ ] Set proper file permissions
- [ ] Configure firewall rules
- [ ] Set up log rotation
- [ ] Configure backup for uploads/ directory
- [ ] Update Google OAuth redirect URI to production domain
- [ ] Disable debug mode in production

## Monitoring

Consider adding:
- Application monitoring (Sentry, New Relic)
- Log aggregation (ELK stack, CloudWatch)
- Health check endpoint
- Performance monitoring

## Notes

- The development server (`python app.py`) should **ONLY** be used for local development
- Always use a production WSGI server for any public-facing deployment
- Ensure your hosting platform supports persistent sessions
- Configure proper logging for production debugging

