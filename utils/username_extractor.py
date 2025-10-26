"""
Username Extractor Module
Extracts usernames from filenames following the format:
<username>_<uniqueNumbers>.ext
"""

import re
from pathlib import Path
from typing import Optional

class UsernameExtractor:
    """Handles extracting usernames from image filenames"""
    
    def __init__(self):
        # Pattern to match username before first underscore
        self.username_pattern = re.compile(r'^([^_]+)_\d+\.[a-zA-Z0-9]+$')
    
    def extract_username(self, file_path: str) -> Optional[str]:
        """
        Extract username from filename
        
        Expected format: <username>_<numbers>.ext
        Example: alana_moore_3839299832.jpg -> alana_moore
        
        Args:
            file_path (str): Full path to the file
            
        Returns:
            Optional[str]: Username if found, None otherwise
        """
        try:
            filename = Path(file_path).name
            
            # Find the first underscore followed by numbers
            parts = filename.split('_')
            if len(parts) < 2:
                return None
            
            # Check if the last part (after last underscore) contains numbers and extension
            last_part = parts[-1]
            if not re.match(r'\d+\.[a-zA-Z0-9]+$', last_part):
                return None
            
            # Join all parts except the last one (which contains the numbers)
            username = '_'.join(parts[:-1])
            
            # Validate username (should not be empty and contain reasonable characters)
            if username and re.match(r'^[a-zA-Z0-9_-]+$', username):
                return username
            
            return None
            
        except Exception as e:
            print(f"Error extracting username from {file_path}: {e}")
            return None
    
    def validate_filename_format(self, filename: str) -> bool:
        """
        Validate if filename follows the expected format
        
        Args:
            filename (str): The filename to validate
            
        Returns:
            bool: True if format is valid
        """
        return self.username_pattern.match(filename) is not None