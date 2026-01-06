# Google Workspace SSO Authentication Setup

This document explains how to set up Google Workspace SSO authentication for the Integral ProjectText FileProcessor.

## Overview

The application uses Google OAuth2 for Single Sign-On (SSO) authentication. Users must authenticate with their Google Workspace accounts before accessing the application.

## Prerequisites

- Google Workspace Professional account
- Access to Google Cloud Console
- Python 3.7 or higher

## Setup Instructions

### 1. Create Google OAuth2 Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing project
3. Enable the following APIs:
   - **Google Identity API** (or Google+ API)
   - **People API** (for user profile information)

4. Navigate to **APIs & Services** → **Credentials**
5. Click **Create Credentials** → **OAuth 2.0 Client ID**
6. Configure OAuth consent screen:
   - User Type: **Internal** (for Google Workspace only) or **External**
   - Application name: Integral ProjectText FileProcessor
   - Support email: Your email
   - Scopes: `openid`, `email`, `profile`
   - Save and continue

7. Create OAuth 2.0 Client ID:
   - Application type: **Web application**
   - Name: Integral ProjectText FileProcessor
   - Authorized redirect URIs:
     - Development: `http://localhost:5000/callback`
     - Production: `https://yourdomain.com/callback`
   - Click **Create**

8. Copy the **Client ID** and **Client Secret**

### 2. Configure Environment Variables

Create a `.env` file in the project root (or set environment variables):

```env
SECRET_KEY=your-random-secret-key-here-generate-a-long-random-string
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
```

**Important**: Never commit the `.env` file to version control. It's already in `.gitignore`.

### 3. Generate Secret Key

Generate a secure random secret key:

```python
import secrets
print(secrets.token_hex(32))
```

Or use:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### 4. Install Dependencies

```bash
py -m pip install -r requirements.txt
```

### 5. Run the Application

```bash
py app.py
```

## How It Works

1. **Unauthenticated users** are redirected to `/login`
2. **Login page** displays a "Sign in with Google" button
3. **User clicks** the button and is redirected to Google OAuth
4. **Google authenticates** the user and redirects back to `/callback`
5. **Application** creates a user session and logs the user in
6. **Authenticated users** can access all features
7. **Logout** clears the session and redirects to login

## Security Features

- All routes are protected with `@login_required` decorator
- Session-based authentication using Flask-Login
- Secure session management
- OAuth2 flow for Google authentication
- User information stored in session (not database)

## User Interface

- **Login Page**: Clean, branded login page with Google sign-in button
- **Header**: Shows user name and avatar (if available) with logout button
- **Protected Routes**: All application features require authentication

## Troubleshooting

### "Invalid redirect URI" Error

- Ensure the redirect URI in Google Cloud Console exactly matches: `http://localhost:5000/callback`
- For production, use: `https://yourdomain.com/callback`
- Check for trailing slashes or protocol mismatches

### "Access blocked" Error

- Verify the OAuth consent screen is configured correctly
- Check that the required APIs are enabled
- Ensure the user's email domain matches your Google Workspace domain (if using Internal user type)

### Environment Variables Not Loading

- Ensure `.env` file is in the project root directory
- Check that `python-dotenv` is installed: `py -m pip install python-dotenv`
- Verify variable names match exactly (case-sensitive)

### Session Not Persisting

- Check that `SECRET_KEY` is set and consistent
- Clear browser cookies and try again
- Verify Flask session configuration

## Production Deployment

For production:

1. Set environment variables on your hosting platform
2. Update redirect URI in Google Cloud Console to your production domain
3. Use HTTPS (required for OAuth in production)
4. Set a strong, unique `SECRET_KEY`
5. Consider using environment-specific configuration

## Domain Restriction (Optional)

To restrict access to specific Google Workspace domains:

1. In Google Cloud Console, go to **APIs & Services** → **OAuth consent screen**
2. Under **User type**, select **Internal** (restricts to your organization)
3. Or add domain restrictions in the application code by checking `user.email` domain

## Support

For issues with Google OAuth setup, refer to:
- [Google OAuth 2.0 Documentation](https://developers.google.com/identity/protocols/oauth2)
- [Google Cloud Console Help](https://support.google.com/cloud/answer/6158849)

