# New Features and Security Enhancements

## Security Improvements

### 1. Enhanced File Validation
- **File Signature Verification**: Validates Excel files by checking file headers/signatures
  - `.xlsx` files: Checks for ZIP archive signature (PK\x03\x04)
  - `.xls` files: Checks for OLE2 signature (\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1)
- **Content Validation**: Verifies files can actually be opened as Excel files
- **Prevents**: Malicious file uploads, file type spoofing

### 2. Session Security
- **Shorter Session Timeout**: Reduced from 7 days to 2 hours
- **Proper Session Invalidation**: 
  - Clears all session data on logout
  - Regenerates session ID to prevent session fixation attacks
  - Session marked as non-permanent on logout
- **Prevents**: Session hijacking, unauthorized access from abandoned sessions

### 3. Input Sanitization
- **Enhanced Input Validation**:
  - `sanitize_input()`: Removes control characters, limits length
  - `sanitize_filename()`: Enhanced filename sanitization with length limits
  - `validate_email()`: Email format validation
- **Applied to**: All user inputs (column names, max_chars, filenames)
- **Prevents**: XSS attacks, path traversal, buffer overflows

## Functionality Improvements

### 1. File Preview
- **Modal-based Preview**: Clean, non-intrusive preview interface
- **Features**:
  - Shows first 10 rows and 10 columns
  - Displays sheet name, total rows/columns
  - Scrollable table with hover effects
  - Available for both uploaded and processed files
- **UI**: Modal overlay that doesn't overcrowd the main page
- **Endpoint**: `/preview/<folder>/<filename>`

### 2. Email Notifications
- **Automatic Notifications**: Sends email when file processing completes
- **Email Content**:
  - User-friendly greeting
  - Input and output filenames
  - Processing time
  - Direct download link
- **Configuration**: 
  - Enable/disable via `MAIL_ENABLED` environment variable
  - Configurable SMTP settings
  - Uses Flask-Mail for reliable delivery
- **Error Handling**: Email failures don't break the processing workflow

## Configuration

### Environment Variables

Add to your `.env` file:

```env
# Email Configuration
MAIL_ENABLED=True  # Set to False to disable email notifications
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password  # Use App Password for Gmail
MAIL_DEFAULT_SENDER=your-email@gmail.com

# Base URL for email links
BASE_URL=https://pt.schrack.lastchance.ro  # Production URL
```

### Gmail Setup

For Gmail, you need to:
1. Enable 2-Factor Authentication
2. Generate an App Password: https://myaccount.google.com/apppasswords
3. Use the App Password as `MAIL_PASSWORD`

## Testing

### Local Testing

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure email** (optional for testing):
   - Set `MAIL_ENABLED=True` in `.env`
   - Configure SMTP settings
   - Or leave `MAIL_ENABLED=False` to test without email

3. **Test file validation**:
   - Try uploading a non-Excel file (should be rejected)
   - Try uploading a corrupted Excel file (should be rejected)

4. **Test preview**:
   - Upload a file
   - Click "Preview" button
   - Verify modal shows file content

5. **Test email** (if enabled):
   - Process a file
   - Check email inbox for notification

### Production Deployment

1. **Update requirements**:
   ```bash
   pip install -r requirements-prod.txt
   ```

2. **Configure email** in production `.env`:
   ```env
   MAIL_ENABLED=True
   BASE_URL=https://pt.schrack.lastchance.ro
   # ... other email settings
   ```

3. **Restart service**:
   ```bash
   sudo systemctl restart integral-projecttext
   ```

## Security Notes

- File validation now checks both file signature and ability to open as Excel
- Session timeout reduced to 2 hours for better security
- All inputs are sanitized before processing
- Email notifications include secure download links
- Preview endpoint requires authentication

## Backward Compatibility

- All changes are backward compatible
- Email notifications are opt-in (disabled by default)
- Preview feature is additive (doesn't affect existing functionality)
- Session timeout change applies to new sessions only


