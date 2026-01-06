# Production Deployment Checklist

## ✅ Step 1: SSH Key Setup (COMPLETED)

**SSH Public Key** (copied to clipboard):
```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAINa/bf8BpIEih+QHTRjlgxonGhnCGg2i4KnxJzdtkG2a production-deploy@integral-projecttext
```

**Next**: Add this key to the server's `~/.ssh/authorized_keys` file

## Step 2: Connect to Server

```bash
ssh -p 2324 lastchance@185.125.109.150
# or
ssh -p 2324 lastchance@pt.schrack.lastchance.ro
```

## Step 3: Add SSH Key to Server

Once connected, run:
```bash
mkdir -p ~/.ssh
chmod 700 ~/.ssh
echo "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAINa/bf8BpIEih+QHTRjlgxonGhnCGg2i4KnxJzdtkG2a production-deploy@integral-projecttext" >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

## Step 4: Run Setup Script

Option A - Automated (recommended):
```bash
# Upload setup script to server (you may need sudo access)
scp -P 2324 setup_production.sh lastchance@185.125.109.150:/home/lastchance/
ssh -p 2324 lastchance@185.125.109.150
# If you have sudo access, run:
sudo chmod +x setup_production.sh
sudo ./setup_production.sh
```

Option B - Manual (follow PRODUCTION_SETUP.md):
```bash
# Follow step-by-step instructions in PRODUCTION_SETUP.md
```

## Step 5: Configure Environment Variables

```bash
cd /home/lastchance/app
nano .env
```

Add your Google OAuth credentials:
```env
SECRET_KEY=<already generated>
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
SESSION_COOKIE_SECURE=True
FLASK_DEBUG=False
```

## Step 6: Update Google OAuth Redirect URI

In Google Cloud Console:
1. Go to APIs & Services → Credentials
2. Edit your OAuth 2.0 Client ID
3. Add authorized redirect URI: `https://pt.schrack.lastchance.ro/callback`
4. Save

## Step 7: Set Up SSL Certificate

```bash
sudo certbot --nginx -d pt.schrack.lastchance.ro
```

Follow prompts and select option to redirect HTTP to HTTPS.

## Step 8: Restart Services

```bash
sudo systemctl restart integral-projecttext
sudo systemctl restart nginx
```

## Step 9: Test Application

Visit: https://pt.schrack.lastchance.ro

## Step 10: Merge to Main Branch

Once everything works:

```bash
cd /home/lastchance/app
git checkout main
git merge authentication
git push origin main
```

## Useful Commands

### Check service status:
```bash
sudo systemctl status integral-projecttext
```

### View application logs:
```bash
sudo journalctl -u integral-projecttext -f
```

### View Nginx logs:
```bash
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log
```

### Restart application:
```bash
sudo systemctl restart integral-projecttext
```

### Check if port is listening:
```bash
sudo netstat -tulpn | grep 5000
```

## Troubleshooting

### Service won't start:
- Check logs: `sudo journalctl -u integral-projecttext -n 50`
- Verify .env file exists and has correct values
- Check file permissions: `sudo chown -R lastchance:lastchance /home/lastchance/app`

### Nginx 502 Bad Gateway:
- Verify Gunicorn is running: `sudo systemctl status integral-projecttext`
- Check Gunicorn logs
- Verify proxy_pass URL in Nginx config matches Gunicorn bind address

### SSL Certificate issues:
- Ensure DNS points to server IP
- Check firewall allows port 80 and 443
- Verify domain is accessible: `curl -I http://pt.schrack.lastchance.ro`

