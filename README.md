# Integral ProjectText FileProcessor

**Version 1.0**

A modern, production-ready web application for processing Excel files by splitting long text cells into multiple columns. Designed specifically for processing entity names from Project Text for optimal formatting.

## 🎯 Overview

Integral ProjectText FileProcessor is a Flask-based web application that allows users to upload Excel files, specify processing parameters, and automatically split long text cells into multiple columns. The application features Google OAuth authentication, drag-and-drop file upload, advanced validation, statistics tracking, and a fully localized Romanian interface.

## ✨ Key Features

### 🔐 Authentication & Security
- **Google Workspace SSO Authentication** - Secure login with Google Workspace accounts
- Session-based authentication with 2-hour timeout
- Enhanced file validation (signature verification, content validation)
- Input sanitization to prevent XSS and path traversal attacks
- Secure session management with proper invalidation

### 📤 File Processing
- **Drag and Drop Upload** - Upload files by dragging directly onto the upload area
- **Multiple File Support** - Upload and process multiple files simultaneously
- **Visual Upload Progress** - Real-time progress indicators for each file
- **Excel File Support** - Process both `.xlsx` and `.xls` formats
- **Automatic Text Splitting** - Split long text cells into multiple columns based on character limits
- **Flexible Parameters** - Adjust column name and max characters per cell without re-uploading

### 🔍 Advanced Validation
- **Pre-upload Validation** - Validates file structure before processing
  - Ensures Excel file has only one sheet
  - Validates that data exists in only one column
- **Automatic Parameter Suggestion** - Suggests optimal column and max characters
- **Smart Defaults** - Max characters default set to 20 (range: 18-23)
- **File Signature Verification** - Validates Excel files by checking file headers

### 📊 Statistics Dashboard
- **Total Files Processed** - Track cumulative processing count
- **Average Processing Time** - Monitor performance metrics
- **Processing Success Rate** - Track success/failure statistics
- **Auto-refresh** - Updates every 30 seconds

### 👁️ Preview & Search
- **File Preview** - Preview both input and processed files
- **Pagination for Input Files** - Browse large files with 50 rows per page
- **Search Functionality** - Search within input file preview (client-side filtering)
- **Optimized for Large Files** - Handles files with thousands of rows efficiently
- **Output File Limitation** - Shows first 50 rows of processed files with total count notification

### 📧 Email Notifications
- **Automatic Notifications** - Email sent when file processing completes
- **Beautiful HTML Templates** - Optimized for Gmail web app
- **Romanian Content** - All email content in Romanian
- **Direct Download Links** - Secure links to download processed files
- **Processing Details** - Includes input/output filenames and processing time

### 🌐 User Interface
- **Fully Localized** - Complete Romanian interface 
- **Modern, Responsive Design** - Works on desktop and mobile devices
- **Interactive Help System** - FAQ section with expandable questions
- **Step-by-Step Tutorial** - Interactive guide for new users
- **Contextual Tooltips** - Helpful hints throughout the interface
- **Professional Branding** - Custom logos and styling

### 🚀 Performance & Optimization
- **Memory Efficient** - Optimized Excel reading using `iter_rows` for large files
- **Fast Processing** - Efficient text splitting algorithm
- **Scalable Architecture** - Handles files with thousands of rows
- **Production Ready** - Configured for deployment with Gunicorn/Waitress

## 📋 Requirements

- Python 3.7 or higher
- pip (Python package manager)
- Google Cloud Console account (for OAuth setup)
- Gmail account (for email notifications, optional)

## 🛠️ Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd ProjectTextApp
```

### 2. Install Dependencies

For local development:
```bash
pip install -r requirements.txt
```

For production:
```bash
pip install -r requirements-prod.txt
```

### 3. Configure Environment Variables

Copy `config.example.env` to `.env` and configure the following:

```env
# Secret Key (generate a secure random key)
SECRET_KEY=your-secret-key-here

# Google OAuth Configuration
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret

# Email Configuration (optional)
MAIL_ENABLED=True
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=your-email@gmail.com

# Application Settings
BASE_URL=http://localhost:5000  # For production: https://yourdomain.com
FLASK_DEBUG=False  # Set to True for development
SESSION_COOKIE_SECURE=False  # Set to True for HTTPS in production
```

### 4. Set Up Google OAuth

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable Google Identity API
4. Go to **Credentials** → **Create Credentials** → **OAuth 2.0 Client ID**
5. Set **Application type** to "Web application"
6. Add **Authorized redirect URIs**:
   - For local development: `http://localhost:5000/callback`
   - For production: `https://yourdomain.com/callback`
7. Copy the **Client ID** and **Client Secret** to your `.env` file

### 5. Set Up Gmail (Optional)

For email notifications:
1. Enable 2-Factor Authentication on your Gmail account
2. Generate an App Password: https://myaccount.google.com/apppasswords
3. Use the App Password as `MAIL_PASSWORD` in your `.env` file

## 🚀 Running the Application

### Local Development

**Windows:**
```bash
py app.py
```

**Linux/Mac:**
```bash
python3 app.py
```

The application will start on `http://localhost:5000`

### Production Deployment

See `PRODUCTION_SETUP.md` and `PRODUCTION_DEPLOYMENT_CHECKLIST.md` for detailed deployment instructions.

Quick start with Gunicorn:
```bash
gunicorn -c gunicorn_config.py wsgi:app
```

Or with Waitress (Windows):
```bash
waitress-serve --host=0.0.0.0 --port=5000 wsgi:app
```

## 📖 Usage

1. **Login**: Access the application and sign in with your Google Workspace account
2. **Upload Files**: 
   - Drag and drop files onto the upload area, or
   - Click to browse and select Excel files
3. **Configure Parameters**: 
   - Enter the column letter to process (e.g., A, B, C)
   - Set maximum characters per cell (default: 20, range: 18-23)
   - Adjust parameters without re-uploading if needed
4. **Process**: Click the "Process" button next to each uploaded file
5. **Preview**: Click "Preview" to view file contents before or after processing
6. **Download**: Download processed files from the "Generated Output" section
7. **Monitor**: View processing statistics in the dashboard
8. **Get Help**: Access FAQ and tutorial from the Help section

## 📁 Project Structure

```
.
├── app.py                          # Main Flask application
├── split.py                        # Core text splitting logic
├── wsgi.py                         # WSGI entry point for production
├── gunicorn_config.py              # Gunicorn configuration
├── requirements.txt                # Development dependencies
├── requirements-prod.txt           # Production dependencies
├── config.example.env              # Environment variables template
├── .gitignore                      # Git ignore rules
├── README.md                       # This file
├── templates/                      # HTML templates
│   ├── index.html                  # Main application interface
│   └── login.html                  # Login page
├── static/                         # Static files
│   ├── css/
│   │   └── style.css               # Application styles
│   └── images/                     # Logo and icon files
├── uploads/                        # Uploaded files (auto-created)
├── outputs/                        # Processed files (auto-created)
└── processing_stats.json           # Statistics data (auto-created)
```

## 🔧 Configuration

### File Size Limits
- Maximum file size: 16MB
- Preview limit: 500 rows for input files, 50 rows for output files
- Search limit: 2000 rows for input files

### Processing Parameters
- **Max Characters**: Range 18-23, default 20
- **Column Validation**: Must be a valid Excel column letter (A-Z, AA-ZZ, etc.)

### Session Settings
- Session timeout: 2 hours
- Secure cookies: Enabled in production (HTTPS)

## 🧪 Testing

### Local Testing Checklist

- [ ] Google OAuth login works
- [ ] File upload (drag-and-drop and browse) works
- [ ] File validation rejects invalid files
- [ ] Parameter adjustment works without re-upload
- [ ] File processing completes successfully
- [ ] Preview shows correct data with pagination
- [ ] Search works in input file preview
- [ ] Output files show only first 50 rows
- [ ] Statistics dashboard displays and updates
- [ ] Email notifications are sent (if enabled)
- [ ] Download links work correctly

## 📝 API Endpoints

- `GET /` - Main application page
- `GET /login` - Login page
- `GET /callback` - OAuth callback handler
- `GET /logout` - Logout handler
- `POST /api/upload` - File upload endpoint
- `POST /api/process` - File processing endpoint
- `GET /api/preview/<folder>/<filename>` - File preview endpoint
- `GET /api/download/<folder>/<filename>` - File download endpoint
- `GET /api/statistics` - Statistics endpoint
- `POST /api/validate-file` - File validation endpoint

## 🔒 Security Features

- File signature verification
- Content validation
- Input sanitization
- Session security (2-hour timeout)
- Secure session invalidation on logout
- XSS protection
- Path traversal prevention

## 🌍 Localization

The application interface is fully localized in Romanian


## 📊 Statistics Tracking

The application automatically tracks:
- Total number of files processed
- Average processing time
- Success/failure rate

Statistics are stored in `processing_stats.json` and updated in real-time.

## 🐛 Troubleshooting

### "Invalid redirect URI" Error
- Ensure redirect URI in Google Cloud Console exactly matches your callback URL
- Check for trailing slashes or protocol mismatches

### "ModuleNotFoundError" in Production
- Ensure all dependencies are installed: `pip install -r requirements-prod.txt`
- Verify virtual environment is activated

### Email Not Sending
- Verify Gmail App Password is correct
- Check `MAIL_ENABLED=True` in `.env`
- Verify SMTP settings are correct

### Preview Not Working
- Check browser console for JavaScript errors
- Verify file is not too large (preview limited to 500 rows for input files)
- Ensure user is authenticated

### File Processing Fails
- Verify file has only one sheet
- Ensure data exists in only one column
- Check file is not corrupted
- Verify column name is valid

## 📄 License

[Specify your license here]

## 👥 Contributing

[Add contribution guidelines if applicable]

## 📞 Support

For issues, questions, or feature requests, please [create an issue](link-to-issues) or contact the development team.

## 🎉 Version History

### Version 1.0 (Current)
- Initial production release
- Google OAuth authentication
- Drag-and-drop file upload
- Advanced validation and parameter suggestion
- Statistics dashboard
- Preview with pagination and search
- HTML email notifications
- Full Romanian localization
- Help & FAQ system
- Production-ready deployment configuration

---

**Integral ProjectText FileProcessor** - Process Excel files by splitting long text cells efficiently and securely.
