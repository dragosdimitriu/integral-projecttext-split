# Integral ProjectText FileProcessor

A modern web application for processing Excel files by splitting long text cells into multiple columns.

## Features

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

1. **Upload File**: Click "Choose File" and select an Excel file (.xlsx or .xls)
2. **Enter Column**: Specify the column letter to process (e.g., A, B, C)
3. **Set Max Characters**: Enter the maximum number of characters allowed per cell
4. **Upload**: Click "Upload File" button
5. **Process**: Click the "Process" button next to the uploaded file
6. **Download**: Once processing is complete, download the generated file from the "Generated Output" section

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

