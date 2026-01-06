import os
import time
import re
import struct
from flask import Flask, render_template, request, jsonify, send_file, session, redirect, url_for
from werkzeug.utils import secure_filename
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from authlib.integrations.flask_client import OAuth
from flask_mail import Mail, Message
from dotenv import load_dotenv
from datetime import datetime, timedelta
import split
import uuid
import openpyxl

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24).hex())

# Session configuration
# Set SESSION_COOKIE_SECURE=True in production when using HTTPS
app.config['SESSION_COOKIE_SECURE'] = os.environ.get('SESSION_COOKIE_SECURE', 'False').lower() == 'true'
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
# Shorter session timeout: 2 hours (was 7 days)
app.permanent_session_lifetime = timedelta(hours=2)

# Google OAuth Configuration
app.config['GOOGLE_CLIENT_ID'] = os.environ.get('GOOGLE_CLIENT_ID', '')
app.config['GOOGLE_CLIENT_SECRET'] = os.environ.get('GOOGLE_CLIENT_SECRET', '')
app.config['GOOGLE_DISCOVERY_URL'] = "https://accounts.google.com/.well-known/openid-configuration"

app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'outputs'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Email configuration
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'True').lower() == 'true'
app.config['MAIL_USE_SSL'] = os.environ.get('MAIL_USE_SSL', 'False').lower() == 'true'
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', '')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', '')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', '')
app.config['MAIL_ENABLED'] = os.environ.get('MAIL_ENABLED', 'False').lower() == 'true'

# Initialize Flask-Mail
mail = Mail(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

# Initialize OAuth
oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=app.config['GOOGLE_CLIENT_ID'],
    client_secret=app.config['GOOGLE_CLIENT_SECRET'],
    server_metadata_url=app.config['GOOGLE_DISCOVERY_URL'],
    client_kwargs={
        'scope': 'openid email profile',
        'prompt': 'select_account'
    }
)

# User class for Flask-Login
class User(UserMixin):
    def __init__(self, id, email, name, picture):
        self.id = id
        self.email = email
        self.name = name
        self.picture = picture

@login_manager.user_loader
def load_user(user_id):
    # Load user from session
    if 'user_info' in session:
        user_info = session['user_info']
        # Verify the user_id matches
        if user_info.get('id') == user_id:
            return User(
                id=user_info['id'],
                email=user_info['email'],
                name=user_info['name'],
                picture=user_info.get('picture', '')
            )
    return None

# Create necessary directories
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'xlsx', 'xls'}
MAX_COLUMN_LENGTH = 3  # Maximum column name length (e.g., "ZZZ")
MAX_CHARS_LIMIT = 10000  # Maximum characters per cell limit
MIN_CHARS_LIMIT = 1  # Minimum characters per cell limit

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_column_name(column):
    """Validate column name format (only letters, max 3 characters)"""
    if not column:
        return False, "Column name cannot be empty"
    if len(column) > MAX_COLUMN_LENGTH:
        return False, f"Column name must be {MAX_COLUMN_LENGTH} characters or less"
    if not re.match(r'^[A-Z]+$', column):
        return False, "Column name must contain only uppercase letters (A-Z)"
    return True, None

def validate_max_chars(max_chars):
    """Validate max_chars is within reasonable bounds"""
    if max_chars < MIN_CHARS_LIMIT:
        return False, f"Max characters must be at least {MIN_CHARS_LIMIT}"
    if max_chars > MAX_CHARS_LIMIT:
        return False, f"Max characters cannot exceed {MAX_CHARS_LIMIT}"
    return True, None

def validate_excel_file(filepath):
    """Validate that the file is a valid Excel file"""
    try:
        wb = openpyxl.load_workbook(filepath, read_only=True, data_only=True)
        wb.close()
        return True, None
    except Exception as e:
        return False, f"Invalid Excel file: {str(e)}"

def validate_file_content(filepath):
    """Enhanced file validation: Check file signature/MIME type"""
    try:
        with open(filepath, 'rb') as f:
            # Read first 8 bytes to check file signature
            header = f.read(8)
            
            # Excel file signatures:
            # .xlsx: PK\x03\x04 (ZIP archive, Excel 2007+)
            # .xls: \xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1 (OLE2, Excel 97-2003)
            
            if len(header) < 8:
                return False, "File too small or corrupted"
            
            # Check for .xlsx (ZIP-based format)
            if header[:2] == b'PK':
                # Verify it's actually a ZIP file
                if header[2:4] == b'\x03\x04':
                    return True, None
            
            # Check for .xls (OLE2 format)
            if header[:8] == b'\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1':
                return True, None
            
            return False, "File does not appear to be a valid Excel file (invalid file signature)"
    except Exception as e:
        return False, f"Error reading file: {str(e)}"

def sanitize_filename(filename):
    """Additional sanitization for filename"""
    # Remove any path components
    filename = os.path.basename(filename)
    # Remove any dangerous characters (keep only alphanumeric, dots, underscores, hyphens)
    filename = re.sub(r'[^a-zA-Z0-9._-]', '', filename)
    # Limit filename length
    if len(filename) > 255:
        name, ext = os.path.splitext(filename)
        filename = name[:255-len(ext)] + ext
    return filename

def sanitize_input(text, max_length=100):
    """Sanitize and validate text input"""
    if not text:
        return None
    # Remove leading/trailing whitespace
    text = text.strip()
    # Limit length
    if len(text) > max_length:
        text = text[:max_length]
    # Remove any control characters
    text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
    return text

def validate_email(email):
    """Validate email format"""
    if not email:
        return False
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

@app.route('/')
@login_required
def index():
    # Ensure user is properly loaded
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    return render_template('index.html', user=current_user)

@app.route('/login')
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/auth/google')
def google_login():
    redirect_uri = url_for('callback', _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route('/callback')
def callback():
    try:
        token = google.authorize_access_token()
        
        if not token:
            return render_template('login.html', error="Failed to get access token from Google"), 400
        
        # Fetch user info from Google - Authlib handles the userinfo endpoint automatically
        # Try using the token directly with the userinfo endpoint
        resp = google.get('https://www.googleapis.com/oauth2/v2/userinfo', token=token)
        
        if resp.status_code != 200:
            # Try alternative endpoint
            resp = google.get('https://openidconnect.googleapis.com/v1/userinfo', token=token)
            if resp.status_code != 200:
                return render_template('login.html', error=f"Failed to fetch user info: HTTP {resp.status_code}"), 400
        
        user_info = resp.json()
        
        # Create user object - handle both 'sub' and 'id' fields
        user_id = user_info.get('sub') or user_info.get('id', '')
        if not user_id:
            return render_template('login.html', error="Failed to get user ID from Google"), 400
        
        user_email = user_info.get('email', '')
        user_name = user_info.get('name', user_email or 'Unknown')
        user_picture = user_info.get('picture', '')
        
        # Create user object
        user = User(
            id=user_id,
            email=user_email,
            name=user_name,
            picture=user_picture
        )
        
        # Store user info in session BEFORE login_user
        session['user_info'] = {
            'id': user.id,
            'email': user.email,
            'name': user.name,
            'picture': user.picture
        }
        
        # Make session permanent (2 hour timeout)
        session.permanent = True
        
        # Login the user (don't use remember=True to enforce session timeout)
        login_user(user, remember=False)
        
        return redirect(url_for('index'))
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Authentication error: {error_details}")  # Debug output
        return render_template('login.html', error=f"Error during authentication: {str(e)}"), 400

@app.route('/logout')
@login_required
def logout():
    # Properly invalidate session
    user_id = current_user.id if current_user.is_authenticated else None
    logout_user()
    session.clear()
    # Regenerate session ID to prevent session fixation
    session.permanent = False
    return redirect(url_for('login'))

@app.route('/upload', methods=['POST'])
@login_required
def upload_file():
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file provided'}), 400
    
    file = request.files['file']
    # Enhanced input sanitization
    column = sanitize_input(request.form.get('column', ''), max_length=3)
    if column:
        column = column.upper()
    max_chars = sanitize_input(request.form.get('max_chars', ''), max_length=10)
    
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No file selected'}), 400
    
    # Validate file extension
    if not allowed_file(file.filename):
        return jsonify({'success': False, 'error': 'Invalid file type. Please upload .xlsx or .xls files'}), 400
    
    # Validate and sanitize column name
    is_valid, error_msg = validate_column_name(column)
    if not is_valid:
        return jsonify({'success': False, 'error': error_msg}), 400
    
    # Validate max_chars
    try:
        max_chars = int(max_chars)
        is_valid, error_msg = validate_max_chars(max_chars)
        if not is_valid:
            return jsonify({'success': False, 'error': error_msg}), 400
    except (ValueError, TypeError):
        return jsonify({'success': False, 'error': 'Invalid max characters value. Must be a number.'}), 400
    
    # Sanitize filename
    original_filename = sanitize_filename(secure_filename(file.filename))
    if not original_filename:
        return jsonify({'success': False, 'error': 'Invalid filename'}), 400
    
    # Generate unique filename to avoid conflicts
    file_id = str(uuid.uuid4())
    filename = f"{file_id}_{original_filename}"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    # Ensure path is within upload folder (prevent path traversal)
    filepath = os.path.normpath(filepath)
    if not filepath.startswith(os.path.normpath(app.config['UPLOAD_FOLDER'])):
        return jsonify({'success': False, 'error': 'Invalid file path'}), 400
    
    try:
        file.save(filepath)
        
        # Enhanced file validation: Check file content/signature
        is_valid, error_msg = validate_file_content(filepath)
        if not is_valid:
            # Clean up invalid file
            try:
                os.remove(filepath)
            except:
                pass
            return jsonify({'success': False, 'error': error_msg}), 400
        
        # Validate that the file is actually a valid Excel file (can be opened)
        is_valid, error_msg = validate_excel_file(filepath)
        if not is_valid:
            # Clean up invalid file
            try:
                os.remove(filepath)
            except:
                pass
            return jsonify({'success': False, 'error': error_msg}), 400
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Error saving file: {str(e)}'}), 500
    
    return jsonify({
        'success': True,
        'file_id': file_id,
        'filename': original_filename,
        'uploaded_filename': filename,
        'column': column,
        'max_chars': max_chars,
        'upload_time': datetime.now().isoformat()
    })

@app.route('/process', methods=['POST'])
@login_required
def process_file():
    data = request.json
    if not data:
        return jsonify({'success': False, 'error': 'Invalid request data'}), 400
    
    # Enhanced input sanitization
    uploaded_filename = sanitize_input(data.get('uploaded_filename'), max_length=300)
    column = sanitize_input(data.get('column'), max_length=3)
    if column:
        column = column.upper()
    max_chars_str = sanitize_input(data.get('max_chars'), max_length=10)
    
    if not all([uploaded_filename, column, max_chars_str]):
        return jsonify({'success': False, 'error': 'Missing required parameters'}), 400
    
    # Validate column name again
    is_valid, error_msg = validate_column_name(column)
    if not is_valid:
        return jsonify({'success': False, 'error': error_msg}), 400
    
    # Validate max_chars again
    try:
        max_chars = int(max_chars_str)
        is_valid, error_msg = validate_max_chars(max_chars)
        if not is_valid:
            return jsonify({'success': False, 'error': error_msg}), 400
    except (ValueError, TypeError):
        return jsonify({'success': False, 'error': 'Invalid max characters value'}), 400
    
    # Sanitize filename to prevent path traversal
    uploaded_filename = sanitize_filename(uploaded_filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_filename)
    
    # Ensure path is within upload folder (prevent path traversal)
    filepath = os.path.normpath(filepath)
    if not filepath.startswith(os.path.normpath(app.config['UPLOAD_FOLDER'])):
        return jsonify({'success': False, 'error': 'Invalid file path'}), 400
    
    if not os.path.exists(filepath):
        return jsonify({'success': False, 'error': 'File not found'}), 404
    
    try:
        # Start timing
        start_time = time.time()
        
        # Process the file using split.py
        success, message, output_filename = split.main(filepath, column, max_chars)
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        if success:
            # Move output file to outputs folder
            if output_filename and os.path.exists(output_filename):
                output_basename = os.path.basename(output_filename)
                output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_basename)
                os.rename(output_filename, output_path)
                
                # Send email notification if enabled
                if app.config['MAIL_ENABLED'] and current_user.is_authenticated:
                    try:
                        send_processing_complete_email(
                            current_user.email,
                            current_user.name,
                            uploaded_filename,
                            output_basename,
                            round(processing_time, 2)
                        )
                    except Exception as e:
                        # Don't fail the request if email fails
                        print(f"Failed to send email notification: {str(e)}")
                
                return jsonify({
                    'success': True,
                    'message': message,
                    'output_filename': output_basename,
                    'processing_time': round(processing_time, 2)
                })
            else:
                return jsonify({'success': False, 'error': 'Output file was not created'}), 500
        else:
            return jsonify({'success': False, 'error': message}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

def send_processing_complete_email(user_email, user_name, input_filename, output_filename, processing_time):
    """Send email notification when processing completes"""
    if not app.config['MAIL_ENABLED']:
        return
    
    try:
        # Get base URL from environment or use default
        base_url = os.environ.get('BASE_URL', '')
        if not base_url:
            try:
                base_url = request.host_url.rstrip('/')
            except:
                base_url = 'https://pt.schrack.lastchance.ro'
        
        download_url = f"{base_url}/download/outputs/{output_filename}"
        
        subject = f"File Processing Complete: {input_filename}"
        body = f"""Hello {user_name},

Your file has been processed successfully!

Input File: {input_filename}
Output File: {output_filename}
Processing Time: {processing_time} seconds

Download your processed file:
{download_url}

This link will remain valid for 7 days.

Best regards,
Integral ProjectText FileProcessor"""
        
        msg = Message(
            subject=subject,
            recipients=[user_email],
            body=body,
            sender=app.config['MAIL_DEFAULT_SENDER'] or app.config['MAIL_USERNAME']
        )
        mail.send(msg)
    except Exception as e:
        # Don't raise - email failure shouldn't break the request
        print(f"Error sending email notification: {str(e)}")

@app.route('/preview/<folder>/<filename>')
@login_required
def preview_file(folder, filename):
    """Preview Excel file - return first few rows as JSON"""
    if folder not in ['uploads', 'outputs']:
        return jsonify({'error': 'Invalid folder'}), 400
    
    # Sanitize filename to prevent path traversal
    filename = sanitize_filename(filename)
    filepath = os.path.join(folder, filename)
    
    # Ensure path is within allowed folder (prevent path traversal)
    filepath = os.path.normpath(filepath)
    allowed_path = os.path.normpath(folder)
    if not filepath.startswith(allowed_path):
        return jsonify({'error': 'Invalid file path'}), 400
    
    if not os.path.exists(filepath):
        return jsonify({'error': 'File not found'}), 404
    
    try:
        # Load workbook and get first sheet
        wb = openpyxl.load_workbook(filepath, read_only=True, data_only=True)
        sheet = wb.active
        
        # Get preview data (first 10 rows, first 10 columns)
        preview_data = []
        max_rows = min(10, sheet.max_row)
        max_cols = min(10, sheet.max_column)
        
        for row_idx in range(1, max_rows + 1):
            row_data = []
            for col_idx in range(1, max_cols + 1):
                cell = sheet.cell(row=row_idx, column=col_idx)
                # Get cell value, limit string length for preview
                value = cell.value
                if isinstance(value, str) and len(value) > 50:
                    value = value[:50] + '...'
                row_data.append(str(value) if value is not None else '')
            preview_data.append(row_data)
        
        wb.close()
        
        return jsonify({
            'success': True,
            'filename': filename,
            'sheet_name': sheet.title,
            'total_rows': sheet.max_row,
            'total_columns': sheet.max_column,
            'preview_rows': max_rows,
            'preview_columns': max_cols,
            'data': preview_data
        })
    except Exception as e:
        return jsonify({'error': f'Error reading file: {str(e)}'}), 500

@app.route('/download/<folder>/<filename>')
@login_required
def download_file(folder, filename):
    if folder not in ['uploads', 'outputs']:
        return jsonify({'error': 'Invalid folder'}), 400
    
    # Sanitize filename to prevent path traversal
    filename = sanitize_filename(filename)
    filepath = os.path.join(folder, filename)
    
    # Ensure path is within allowed folder (prevent path traversal)
    filepath = os.path.normpath(filepath)
    allowed_path = os.path.normpath(folder)
    if not filepath.startswith(allowed_path):
        return jsonify({'error': 'Invalid file path'}), 400
    
    if not os.path.exists(filepath):
        return jsonify({'error': 'File not found'}), 404
    
    return send_file(filepath, as_attachment=True)

if __name__ == '__main__':
    # Development server only - DO NOT use in production!
    # Use gunicorn, waitress, or another WSGI server for production
    # See DEPLOYMENT.md for production deployment instructions
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(debug=debug_mode, host='0.0.0.0', port=5000)

