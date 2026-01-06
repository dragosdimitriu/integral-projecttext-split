# Integral ProjectText FileProcessor

A modern web application for processing Excel files by splitting long text cells into multiple columns.

## Features

- **Google Workspace SSO Authentication** - Secure login with Google Workspace accounts
- Upload Excel files (.xlsx or .xls)
- Specify column to process and maximum character length
- Process files with automatic text splitting
- Download processed files
- Modern, responsive web interface
- Cross-platform (Windows and Linux compatible)

## Installation

### Prerequisites

- Python 3.7 or higher
- pip (Python package manager)

### Setup

1. Install dependencies:
```bash
py -m pip install -r requirements.txt
```

2. Configure Google OAuth2:
   - Copy `config.example.env` to `.env` (or set environment variables)
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select an existing one
   - Enable Google+ API (or Google Identity API)
   - Go to **Credentials** → **Create Credentials** → **OAuth 2.0 Client ID**
   - Set **Application type** to "Web application"
   - Add **Authorized redirect URIs**: 
     - For local development: `http://localhost:5000/callback`
     - For production: `https://yourdomain.com/callback`
   - Copy the **Client ID** and **Client Secret** to your `.env` file

3. Set environment variables:
   ```bash
   # Windows PowerShell
   $env:SECRET_KEY="your-secret-key-here"
   $env:GOOGLE_CLIENT_ID="your-client-id.apps.googleusercontent.com"
   $env:GOOGLE_CLIENT_SECRET="your-client-secret"
   
   # Linux/Mac
   export SECRET_KEY="your-secret-key-here"
   export GOOGLE_CLIENT_ID="your-client-id.apps.googleusercontent.com"
   export GOOGLE_CLIENT_SECRET="your-client-secret"
   ```
   
   Or create a `.env` file (make sure it's in `.gitignore`):
   ```
   SECRET_KEY=your-secret-key-here
   GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
   GOOGLE_CLIENT_SECRET=your-client-secret
   ```

## Running the Application

### Windows
```bash
py app.py
```

### Linux/Mac
```bash
python3 app.py
```

The application will start on `http://localhost:5000`

Open your web browser and navigate to `http://localhost:5000` to use the application.

## Usage

1. **Login**: When you first access the application, you'll be redirected to login with your Google Workspace account
2. **Upload File**: Click "Choose File" and select an Excel file (.xlsx or .xls)
3. **Enter Column**: Specify the column letter to process (e.g., A, B, C)
4. **Set Max Characters**: Enter the maximum number of characters allowed per cell
5. **Upload**: Click "Upload File" button
6. **Process**: Click the "Process" button next to the uploaded file
7. **Download**: Once processing is complete, download the generated file from the "Generated Output" section
8. **Logout**: Click the "Logout" button in the top right corner when done

## File Structure

```
.
├── app.py              # Flask web application
├── split.py            # Core processing logic
├── requirements.txt    # Python dependencies
├── README.md          # This file
├── templates/         # HTML templates
│   └── index.html
├── static/            # Static files
│   ├── css/
│   │   └── style.css
│   └── images/        # Image files (logo.png and icon.png)
├── uploads/           # Uploaded files (created automatically)
└── outputs/           # Processed files (created automatically)
```

## Notes

- Processing typically takes 5-10 seconds depending on file size
- The application automatically creates `uploads/` and `outputs/` directories
- Maximum file size is 16MB
- Processed files are saved with "_ProjectTextReady.xlsx" suffix
- **Image Files**: Add `logo.png` (SCHRACK SECONET logo) and `icon.png` (letter "C" icon) to the `static/images/` directory for full branding

## Troubleshooting

- Ensure all dependencies are installed: `py -m pip install -r requirements.txt`
- Make sure port 5000 is available
- Check that uploaded files are valid Excel files (.xlsx or .xls)
- Verify column names are valid (single letter or letter combinations like AA, AB)

