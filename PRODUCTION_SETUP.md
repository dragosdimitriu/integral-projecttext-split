# Production Server Setup Guide

## Server Information
- **IP Address**: 185.125.109.150
- **Domain**: pt.schrack.lastchance.ro
- **SSH Port**: 2324
- **User**: lastchance (has root/sudo privileges)
- **Google OAuth**: Already registered

## Step 1: SSH Key Setup (Local)

SSH key has been generated. Add the public key to the server:

```bash
# Copy the public key content from above
# Then on the server, add it to authorized_keys:
mkdir -p ~/.ssh
chmod 700 ~/.ssh
echo "YOUR_PUBLIC_KEY_HERE" >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

## Step 2: Initial Server Setup (Run on Server)

### Connect to server:
```bash
ssh -p 2324 lastchance@185.125.109.150
# or
ssh -p 2324 lastchance@pt.schrack.lastchance.ro
```

**Note**: The `lastchance` user has root/sudo privileges, so you can run all commands directly or with `sudo`.

### Update system:
```bash
sudo apt update && sudo apt upgrade -y
```

### Install required packages:
```bash
sudo apt install -y python3 python3-pip python3-venv git nginx supervisor certbot python3-certbot-nginx ufw
```

### Set up firewall:
```bash
sudo ufw allow 2324/tcp  # SSH on custom port
sudo ufw allow 'Nginx Full'
sudo ufw enable
```

## Step 3: Application Setup (Run on Server)

### Clone repository:
```bash
cd /home/lastchance
git clone https://github.com/dragosdimitriu/integral-projecttext-split.git ProjectTextApp
cd ProjectTextApp
git checkout authentication
```

### Create virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements-prod.txt
```

### Create directories:
```bash
mkdir -p uploads outputs
chmod 755 uploads outputs
```

### Create .env file:
```bash
nano .env
```

Add:
```env
SECRET_KEY=GENERATE_A_STRONG_SECRET_KEY_HERE
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-google-client-secret
SESSION_COOKIE_SECURE=True
FLASK_DEBUG=False
```

Generate secret key:
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

## Step 4: Configure Gunicorn

### Create Gunicorn config:
```bash
nano /home/lastchance/ProjectTextApp/gunicorn_config.py
```

Add:
```python
bind = "127.0.0.1:5000"
workers = 4
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2
max_requests = 1000
max_requests_jitter = 100
preload_app = True
```

## Step 5: Create Systemd Service

### Create service file:
```bash
sudo nano /etc/systemd/system/integral-projecttext.service
```

Add:
```ini
[Unit]
Description=Integral ProjectText FileProcessor Gunicorn daemon
After=network.target

[Service]
User=lastchance
Group=lastchance
WorkingDirectory=/home/lastchance/ProjectTextApp
Environment="PATH=/home/lastchance/ProjectTextApp/venv/bin"
EnvironmentFile=/home/lastchance/ProjectTextApp/.env
ExecStart=/home/lastchance/ProjectTextApp/venv/bin/gunicorn --config /home/lastchance/ProjectTextApp/gunicorn_config.py wsgi:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Enable and start service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable integral-projecttext
sudo systemctl start integral-projecttext
sudo systemctl status integral-projecttext
```

## Step 6: Configure Nginx

### Option A: Automated HTTPS Setup (Recommended)

Run the HTTPS setup script:
```bash
cd /home/lastchance/ProjectTextApp
chmod +x setup_https.sh
sudo ./setup_https.sh
```

This will:
- Configure Nginx for HTTPS
- Obtain SSL certificate from Let's Encrypt
- Set up HTTP to HTTPS redirect
- Configure security headers

### Option B: Manual Setup

#### Step 6a: Initial HTTP Configuration

Create Nginx config:
```bash
sudo nano /etc/nginx/sites-available/integral-projecttext
```

Add:
```nginx
server {
    listen 80;
    listen [::]:80;
    server_name pt.schrack.lastchance.ro 185.125.109.150;

    client_max_body_size 16M;

    # Allow Let's Encrypt verification
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }

    # Flask serves static files from /static (no trailing slash)
    location /static {
        alias /home/lastchance/ProjectTextApp/static;
        expires 30d;
        add_header Cache-Control "public";
    }

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
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/integral-projecttext /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### Step 6b: SSL Certificate (Let's Encrypt)

Install Certbot (if not already installed):
```bash
sudo apt-get update
sudo apt-get install -y certbot python3-certbot-nginx
```

Obtain SSL certificate:
```bash
sudo certbot --nginx -d pt.schrack.lastchance.ro --non-interactive --agree-tos --email admin@lastchance.ro --redirect
```

Certbot will automatically:
- Obtain SSL certificate
- Update Nginx configuration for HTTPS
- Set up HTTP to HTTPS redirect
- Configure SSL settings

#### Step 6c: Verify HTTPS Configuration

After Certbot, your Nginx config should look like:
```nginx
# HTTP server - redirect to HTTPS
server {
    listen 80;
    listen [::]:80;
    server_name pt.schrack.lastchance.ro 185.125.109.150;
    return 301 https://$server_name$request_uri;
}

# HTTPS server
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name pt.schrack.lastchance.ro 185.125.109.150;

    ssl_certificate /etc/letsencrypt/live/pt.schrack.lastchance.ro/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/pt.schrack.lastchance.ro/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    client_max_body_size 16M;

    location /static {
        alias /home/lastchance/ProjectTextApp/static;
        expires 30d;
        add_header Cache-Control "public";
    }

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
```

## Step 7: Update Environment Variables for HTTPS

Update `.env` file to enable secure cookies:
```bash
nano /home/lastchance/ProjectTextApp/.env
```

Make sure `SESSION_COOKIE_SECURE=True`:
```env
SECRET_KEY=your-secret-key
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
SESSION_COOKIE_SECURE=True
FLASK_DEBUG=False
```

Restart the service:
```bash
sudo systemctl restart integral-projecttext
```

## Step 8: Update Google OAuth Redirect URI

In Google Cloud Console, update the authorized redirect URI to:
```
https://pt.schrack.lastchance.ro/callback
```

## Step 9: Final Checks

### Check application logs:
```bash
sudo journalctl -u integral-projecttext -f
```

### Check Nginx logs:
```bash
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log
```

### Test application:
Visit: https://pt.schrack.lastchance.ro

## Step 10: Merge to Main (After Testing)

Once everything works:

```bash
cd /home/appuser/app
git checkout main
git merge authentication
git push origin main
```

## Troubleshooting

### Service won't start:
```bash
sudo journalctl -u integral-projecttext -n 50
```

### Permission issues:
```bash
sudo chown -R lastchance:lastchance /home/lastchance/ProjectTextApp
```

### Port already in use:
```bash
sudo netstat -tulpn | grep 5000
```

### Nginx 502 Bad Gateway:
- Check if Gunicorn is running: `sudo systemctl status integral-projecttext`
- Check Gunicorn logs
- Verify proxy_pass URL matches Gunicorn bind address

