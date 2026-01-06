import os
import time
import re
from flask import Flask, render_template, request, jsonify, send_file, session, redirect, url_for
from werkzeug.utils import secure_filename
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from authlib.integrations.flask_client import OAuth
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
app.permanent_session_lifetime = timedelta(days=7)

# Google OAuth Configuration
app.config['GOOGLE_CLIENT_ID'] = os.environ.get('GOOGLE_CLIENT_ID', '')
app.config['GOOGLE_CLIENT_SECRET'] = os.environ.get('GOOGLE_CLIENT_SECRET', '')
app.config['GOOGLE_DISCOVERY_URL'] = "https://accounts.google.com/.well-known/openid-configuration"

app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'outputs'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

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

def sanitize_filename(filename):
    """Additional sanitization for filename"""
    # Remove any path components
    filename = os.path.basename(filename)
    # Remove any dangerous characters
    filename = re.sub(r'[^a-zA-Z0-9._-]', '', filename)
    return filename

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
        
        # Make session permanent
        session.permanent = True
        
        # Login the user
        login_user(user, remember=True)
        
        return redirect(url_for('index'))
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Authentication error: {error_details}")  # Debug output
        return render_template('login.html', error=f"Error during authentication: {str(e)}"), 400

@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    return redirect(url_for('login'))

@app.route('/upload', methods=['POST'])
@login_required
def upload_file():
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file provided'}), 400
    
    file = request.files['file']
    column = request.form.get('column', '').strip().upper()
    max_chars = request.form.get('max_chars', '').strip()
    
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
        
        # Validate that the file is actually a valid Excel file
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
    uploaded_filename = data.get('uploaded_filename')
    column = data.get('column')
    max_chars = data.get('max_chars')
    
    if not all([uploaded_filename, column, max_chars]):
        return jsonify({'success': False, 'error': 'Missing required parameters'}), 400
    
    # Validate column name again
    is_valid, error_msg = validate_column_name(column)
    if not is_valid:
        return jsonify({'success': False, 'error': error_msg}), 400
    
    # Validate max_chars again
    try:
        max_chars = int(max_chars)
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

