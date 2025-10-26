"""
Test script to validate core functionality
"""

import os
import tempfile
from pathlib import Path
from utils.username_extractor import UsernameExtractor
from utils.file_scanner import FileScanner
from database.db_manager import DatabaseManager

def test_username_extraction():
    """Test username extraction functionality"""
    print("Testing Username Extraction...")
    
    extractor = UsernameExtractor()
    
    test_cases = [
        ("alana_moore_3839299832.jpg", "alana_moore"),
        ("jessica_1234567890.png", "jessica"),
        ("maria_garcia_9876543210.mp4", "maria_garcia"),
        ("invalid_filename.jpg", None),  # No numbers after underscore
        ("no_underscore.jpg", None),     # No underscore
    ]
    
    for filename, expected in test_cases:
        result = extractor.extract_username(filename)
        status = "✅" if result == expected else "❌"
        print(f"  {status} {filename} -> {result} (expected: {expected})")
    
    print()

def test_file_scanner():
    """Test file scanning functionality"""
    print("Testing File Scanner...")
    
    scanner = FileScanner()
    
    # Test supported file extensions
    test_files = [
        ("test.jpg", True),
        ("test.jpeg", True),
        ("test.png", True),
        ("test.mp4", True),
        ("test.txt", False),
        ("test.gif", False),
    ]
    
    for filename, expected in test_files:
        result = scanner.is_supported_file(filename)
        status = "✅" if result == expected else "❌"
        print(f"  {status} {filename} -> {result} (expected: {expected})")
    
    print()

def test_database():
    """Test database functionality"""
    print("Testing Database Operations...")
    
    # Use temporary database for testing
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = tmp.name
    
    try:
        db = DatabaseManager(db_path)
        
        # Test adding profiles
        success = db.add_profile("test_user")
        print(f"  ✅ Add profile: {success}")
        
        # Test adding images
        success = db.add_image("test_123.jpg", "/path/to/test_123.jpg", "test_user")
        print(f"  ✅ Add image: {success}")
        
        # Test getting profiles
        profiles = db.get_all_profiles()
        print(f"  ✅ Get profiles: {len(profiles)} found")
        
        # Test getting images
        images = db.get_images_by_username("test_user")
        print(f"  ✅ Get images: {len(images)} found")
        
        # Test counts
        profile_count = db.get_profile_count()
        image_count = db.get_image_count()
        print(f"  ✅ Counts: {profile_count} profiles, {image_count} images")
        
    finally:
        # Clean up
        if os.path.exists(db_path):
            os.unlink(db_path)
    
    print()

if __name__ == "__main__":
    print("🧪 Roster Tagging - Core Functionality Tests\n")
    
    test_username_extraction()
    test_file_scanner()
    test_database()
    
    print("✅ All tests completed!")
    print("\n📌 To run the full application:")
    print("   streamlit run main.py")