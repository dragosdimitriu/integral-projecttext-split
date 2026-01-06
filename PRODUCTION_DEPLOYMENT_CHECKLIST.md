# Production Deployment Checklist

## Pre-Deployment Checklist

### 1. Code Status
- ✅ All changes committed to `main` branch
- ✅ Helper files removed
- ✅ Production dependencies in `requirements-prod.txt`

### 2. Environment Configuration

Update your production `.env` file with:

```env
# Flask Configuration
SECRET_KEY=<generate-strong-random-key>
FLASK_DEBUG=False
SESSION_COOKIE_SECURE=True  # Must be True for HTTPS

# Google OAuth
GOOGLE_CLIENT_ID=<your-client-id>
GOOGLE_CLIENT_SECRET=<your-client-secret>
# Make sure redirect URI in Google Console is: https://pt.schrack.lastchance.ro/callback

# Email Configuration (Gmail SMTP)
MAIL_ENABLED=True
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USE_SSL=False
MAIL_USERNAME=service@lastchance.ro
MAIL_PASSWORD=<gmail-app-password-16-chars>
MAIL_DEFAULT_SENDER=service@lastchance.ro

# Base URL
BASE_URL=https://pt.schrack.lastchance.ro
```

### 3. Gmail App Password Setup

1. Go to: https://myaccount.google.com/security
2. Enable 2-Step Verification (if not already enabled)
3. Go to: https://myaccount.google.com/apppasswords
4. Generate app password for "Mail" → "Other (Custom name)" → "Flask App"
5. Copy the 16-character password (no spaces) to `MAIL_PASSWORD` in `.env`

### 4. Google OAuth Redirect URI

1. Go to: https://console.cloud.google.com/
2. Navigate to: APIs & Services → Credentials
3. Edit your OAuth 2.0 Client ID
4. Add Authorized redirect URI: `https://pt.schrack.lastchance.ro/callback`
5. Save changes

## Deployment Steps

### Step 1: Connect to Production Server

```bash
ssh -p 2324 lastchance@185.125.109.150
# or
ssh -p 2324 lastchance@pt.schrack.lastchance.ro
```

### Step 2: Navigate to Application Directory

```bash
cd /home/lastchance/ProjectTextApp
```

### Step 3: Pull Latest Code

```bash
git fetch origin
git checkout main
git pull origin main
```

### Step 4: Update Dependencies

```bash
source venv/bin/activate
pip install -r requirements-prod.txt
```

### Step 5: Update Environment Variables

```bash
nano .env
# Update all values as per checklist above
# Save and exit (Ctrl+X, Y, Enter)
```

### Step 6: Verify Configuration

```bash
# Check that .env file has correct values
cat .env | grep -E "FLASK_DEBUG|MAIL_ENABLED|BASE_URL"
# Should show:
# FLASK_DEBUG=False
# MAIL_ENABLED=True
# BASE_URL=https://pt.schrack.lastchance.ro
```

### Step 7: Restart Application Service

```bash
sudo systemctl restart integral-projecttext
sudo systemctl status integral-projecttext
```

### Step 8: Check Logs

```bash
# View recent logs
sudo journalctl -u integral-projecttext -n 50 --no-pager

# Follow logs in real-time
sudo journalctl -u integral-projecttext -f
```

### Step 9: Verify Application is Running

```bash
# Check if Gunicorn is running
ps aux | grep gunicorn

# Check if port 5000 is listening
sudo netstat -tlnp | grep 5000
```

### Step 10: Test Application

1. Open browser: https://pt.schrack.lastchance.ro
2. Test login with Google OAuth
3. Upload a test file
4. Process the file
5. Verify email notification is received

## Rollback Procedure

If something goes wrong:

```bash
# Stop the service
sudo systemctl stop integral-projecttext

# Rollback to previous commit
cd /home/lastchance/ProjectTextApp
git log --oneline -5  # Find previous commit
git checkout <previous-commit-hash>

# Restart service
sudo systemctl start integral-projecttext
```

## Post-Deployment Verification

- [ ] Application loads at https://pt.schrack.lastchance.ro
- [ ] Google OAuth login works
- [ ] File upload works
- [ ] File processing works
- [ ] Email notifications are sent
- [ ] Output files can be downloaded
- [ ] No errors in logs

## Troubleshooting

### Application won't start
```bash
# Check service status
sudo systemctl status integral-projecttext

# Check logs for errors
sudo journalctl -u integral-projecttext -n 100
```

### Email not sending
- Verify Gmail app password is correct (16 characters, no spaces)
- Check `MAIL_ENABLED=True` in `.env`
- Check logs for email errors
- Verify `service@lastchance.ro` account has 2FA enabled

### OAuth redirect error
- Verify redirect URI in Google Console matches exactly: `https://pt.schrack.lastchance.ro/callback`
- Check for trailing slashes
- Ensure HTTPS is used (not HTTP)

### Port conflicts
```bash
# Check what's using port 5000
sudo netstat -tlnp | grep 5000

# Kill process if needed (replace PID)
sudo kill -9 <PID>
```

## Service Management

```bash
# Start service
sudo systemctl start integral-projecttext

# Stop service
sudo systemctl stop integral-projecttext

# Restart service
sudo systemctl restart integral-projecttext

# Check status
sudo systemctl status integral-projecttext

# Enable auto-start on boot
sudo systemctl enable integral-projecttext
```

## Important Notes

1. **Never commit `.env` file** - it contains sensitive credentials
2. **Always use HTTPS in production** - `SESSION_COOKIE_SECURE=True`
3. **Keep `FLASK_DEBUG=False` in production** - prevents security issues
4. **Monitor logs regularly** - check for errors or warnings
5. **Backup `.env` file** - store securely, never in git

