# Quick Production Deployment Guide

## 🚀 Fast Setup (5 minutes)

### 1. Add SSH Key to Server
```bash
ssh -p 2324 lastchance@185.125.109.150
mkdir -p ~/.ssh && chmod 700 ~/.ssh
echo "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAINa/bf8BpIEih+QHTRjlgxonGhnCGg2i4KnxJzdtkG2a production-deploy@integral-projecttext" >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

### 2. Upload and Run Setup Script
```bash
# From your local machine
scp -P 2324 setup_production.sh lastchance@185.125.109.150:/home/lastchance/
ssh -p 2324 lastchance@185.125.109.150
# lastchance user has root/sudo privileges
chmod +x setup_production.sh
sudo ./setup_production.sh
```

### 3. Configure Environment
```bash
cd /home/lastchance/ProjectTextApp
nano .env
# Add your GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET
sudo systemctl restart integral-projecttext
```

### 4. Set Up SSL
```bash
sudo certbot --nginx -d pt.schrack.lastchance.ro
```

### 5. Update Google OAuth
- Go to Google Cloud Console
- Add redirect URI: `https://pt.schrack.lastchance.ro/callback`

### 6. Test
Visit: https://pt.schrack.lastchance.ro

## 🔄 Updating Production to Main Branch

After merging to main, update production:

```bash
# SSH to production server
ssh -p 2324 lastchance@185.125.109.150

# Navigate to app directory
cd /home/lastchance/ProjectTextApp

# Switch to main branch and pull latest changes
git checkout main
git pull origin main

# Update dependencies (if requirements changed)
source venv/bin/activate
pip install -r requirements-prod.txt

# Restart the service
sudo systemctl restart integral-projecttext

# Check status
sudo systemctl status integral-projecttext
```

Or use the automated script:
```bash
cd /home/lastchance/ProjectTextApp
chmod +x deploy_main_to_production.sh
sudo ./deploy_main_to_production.sh
```

## 📋 Server Details
- **IP**: 185.125.109.150
- **Domain**: pt.schrack.lastchance.ro
- **SSH Port**: 2324
- **User**: lastchance (has root/sudo privileges)
- **App Path**: /home/lastchance/ProjectTextApp

## 🔧 Common Commands
```bash
# Check status
sudo systemctl status integral-projecttext

# View logs
sudo journalctl -u integral-projecttext -f

# Restart
sudo systemctl restart integral-projecttext

# Update code
cd /home/lastchance/ProjectTextApp
git pull origin authentication
sudo systemctl restart integral-projecttext
```

