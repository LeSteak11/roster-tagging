# Roster Tagging V1

Desktop application for organizing synthetic female model images.

## Overview

This application imports and organizes AI-generated images by extracting usernames from filenames and storing metadata in a local SQLite database.

## Features (V1)

- 📁 **Folder Import**: Scan directories for supported image files
- 🏷️ **Username Extraction**: Parse usernames from filename format `<username>_<numbers>.ext`
- 🗄️ **Database Storage**: Store file metadata in SQLite database
- 🖥️ **Basic UI**: Streamlit-based interface with profiles sidebar

## Supported File Types

- `.jpg`, `.jpeg`, `.png` (images)
- `.mp4` (videos)

## Filename Format

Files must follow this format:
```
<username>_<uniqueNumbers>.ext
```

Examples:
- `alana_moore_3839299832.jpg`
- `jessica_smith_1234567890.png`
- `maria_garcia_9876543210.mp4`

The username is extracted as everything before the first underscore followed by numbers.

## Installation

1. Install Python 3.8+
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

```bash
streamlit run main.py
```

## Project Structure

```
roster-tagging/
├── main.py                 # Main Streamlit application
├── requirements.txt        # Python dependencies
├── database/
│   ├── __init__.py
│   └── db_manager.py      # SQLite database operations
├── utils/
│   ├── __init__.py
│   ├── file_scanner.py    # File scanning functionality
│   └── username_extractor.py  # Username parsing logic
└── README.md
```

## Database Schema

### Profiles Table
- `id` (PK, auto-increment)
- `username` (text, unique)

### Images Table
- `id` (PK, auto-increment)
- `filename` (text)
- `filepath` (text)
- `username` (FK → Profiles.username)
- `date_added` (timestamp, default current)

## Important Notes

- **Fictional Content Only**: All images are assumed to be AI-generated/synthetic
- **Female Models Only**: Application is designed specifically for female AI models
- **No File Movement**: Original files are never moved or altered
- **Path Storage**: Only file paths are stored in database, not the images themselves

## Development Status

✅ **Milestone 0 Complete**
- Project scaffolding
- File scanning and import
- Username extraction
- SQLite database setup
- Basic UI placeholder