import os
import time
import re
from flask import Flask, render_template, request, jsonify, send_file, session
from werkzeug.utils import secure_filename
import split
import uuid
from datetime import datetime
import openpyxl

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'outputs'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

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
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
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
    app.run(debug=True, host='0.0.0.0', port=5000)

