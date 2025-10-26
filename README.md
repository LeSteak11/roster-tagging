# Roster Tagging V2

Desktop application for organizing synthetic female model images with AI-powered tagging.

## Overview

This application imports and organizes AI-generated images by extracting usernames from filenames, storing metadata in a local SQLite database, and automatically tagging images with objective attributes using AI.

## Features (V2)

- 📁 **Folder Import**: Scan directories for supported image files
- 🏷️ **Username Extraction**: Parse usernames from filename format `<username>_<numbers>.ext`
- 🗄️ **Database Storage**: Store file metadata and tags in SQLite database
- 🖥️ **Advanced UI**: Streamlit-based interface with profiles sidebar and image viewer
- 🤖 **AI Tagging**: Automatic attribute extraction using Gemini Vision API
- 📊 **Tag Management**: Review, edit, and validate AI-generated tags
- 🚀 **Batch Processing**: Auto-tag multiple images simultaneously

## Supported File Types

- `.jpg`, `.jpeg`, `.png` (images)
- `.mp4` (videos)

## AI Tag Categories

1. **Hair Color**: blonde, brown, black, red, dyed
2. **Skin Tone**: light, medium, deep
3. **Clothing Type**: sports bra, leggings, shorts, bikini, dress, tank top, crop top, other
4. **Pose Type**: mirror selfie, side pose, front pose, action pose, sitting, standing, other
5. **Environment**: gym, home, beach, studio, outdoor, indoor, other
6. **Face Visibility**: true/false (is face clearly visible?)

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
3. (Optional) Set Gemini API key for AI tagging:
   ```bash
   set GEMINI_API_KEY=your_api_key_here
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
│   ├── username_extractor.py  # Username parsing logic
│   └── ai_tagger.py       # AI tagging with Gemini Vision API
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

### Tags Table (NEW)
- `id` (PK, auto-increment)
- `image_id` (FK → Images.id)
- `hair_color` (text)
- `skin_tone` (text)
- `clothing_type` (text)
- `pose_type` (text)
- `environment` (text)
- `face_visible` (boolean)
- `date_tagged` (timestamp, default current)

## Usage Guide

### Basic Import
1. Enter folder path in sidebar (e.g., `Z:\new guard v1`)
2. Click "Scan Folder" to import images
3. View discovered profiles in sidebar

### Image Viewing
1. Click profile name to view images
2. Click thumbnail to open detailed view
3. Use "Show All Profiles" to return to overview

### AI Tagging
1. Click image thumbnail to open modal
2. Click "🤖 AI Tag" for automatic tagging
3. Review and edit tags using dropdowns
4. Click "💾 Save Tags" to confirm

### Batch Tagging
1. Use "🚀 Auto-tag All Untagged" in sidebar
2. Confirm batch operation
3. Monitor progress bar during processing

## Important Notes

- **Fictional Content Only**: All images are assumed to be AI-generated/synthetic
- **Female Models Only**: Application is designed specifically for female AI models
- **No File Movement**: Original files are never moved or altered
- **Objective Analysis**: AI focuses only on visible, objective attributes
- **Mock Mode**: Without API key, system uses mock tags for testing

## Development Status

✅ **Milestone 2 Complete**
- AI tagging with Gemini Vision API
- Tag review and editing UI
- Batch processing functionality
- Enhanced database schema
- Status notifications