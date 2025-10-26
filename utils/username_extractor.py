"""
Username Extractor Module
Extracts usernames from filenames following the format:
<username>_<uniqueNumbers>.ext

Updated parsing rules:
- Extract everything before the LAST block of digits in the filename
- Remove trailing segments that are purely numbers or timestamp-like
- Preserve underscores that are part of username
- Trim only if > 2 consecutive underscores on ends
"""

import re
from pathlib import Path
from typing import Optional

class UsernameExtractor:
    """Handles extracting usernames from image filenames"""
    
    def __init__(self):
        # Pattern to match digits at the end (before extension)
        self.digit_block_pattern = re.compile(r'_\d+(?=\.[a-zA-Z0-9]+$)')
        # Pattern to match pure number segments
        self.pure_number_pattern = re.compile(r'^_?\d+$')
    
    def extract_username(self, file_path: str) -> Optional[str]:
        """
        Extract username from filename using improved parsing rules
        
        Expected format: <username>_<numbers>.ext
        Examples: 
        - "__ashleesparer___1754697541_3694993242088387086_3400365034.jpg" → "__ashleesparer__"
        - "3masssy_1632363949.jpg" → "3masssy"
        - "1reallykash_1630964335.jpg" → "1reallykash"
        
        Args:
            file_path (str): Full path to the file
            
        Returns:
            Optional[str]: Username if found, None otherwise
        """
        try:
            filename = Path(file_path).name
            
            # Remove file extension
            name_without_ext = Path(filename).stem
            
            # Find all digit blocks at the end
            digit_blocks = []
            temp_name = name_without_ext
            
            # Keep removing digit blocks from the end until we can't find more
            while True:
                match = re.search(r'_(\d+)$', temp_name)
                if not match:
                    break
                digit_blocks.append(match.group(1))
                temp_name = temp_name[:match.start()]
            
            if not digit_blocks:
                # No digit blocks found, this doesn't match our expected format
                return None
            
            # The remaining part is our username candidate
            username_candidate = temp_name
            
            # Clean up the username
            username = self._clean_username(username_candidate)
            
            # Validate the final username
            if self._is_valid_username(username):
                return username
            
            return None
            
        except Exception as e:
            print(f"Error extracting username from {file_path}: {e}")
            return None
    
    def _clean_username(self, username: str) -> str:
        """
        Clean the username by trimming excessive underscores
        
        Args:
            username (str): Raw username to clean
            
        Returns:
            str: Cleaned username
        """
        if not username:
            return username
        
        # Trim leading underscores if more than 2
        while username.startswith('___'):
            username = username[1:]
        
        # Trim trailing underscores if more than 2
        while username.endswith('___'):
            username = username[:-1]
        
        return username
    
    def _is_valid_username(self, username: str) -> bool:
        """
        Validate if the extracted username is reasonable
        
        Args:
            username (str): Username to validate
            
        Returns:
            bool: True if valid
        """
        if not username:
            return False
        
        # Must have at least one non-underscore character
        if username.replace('_', '') == '':
            return False
        
        # Must not be purely numbers
        if re.match(r'^_*\d+_*$', username):
            return False
        
        # Must contain reasonable characters
        if not re.match(r'^[a-zA-Z0-9_-]+$', username):
            return False
        
        # Must not be too short (after removing underscores)
        clean_username = username.strip('_')
        if len(clean_username) < 2:
            return False
        
        return True
    
    def validate_filename_format(self, filename: str) -> bool:
        """
        Validate if filename follows the expected format
        
        Args:
            filename (str): The filename to validate
            
        Returns:
            bool: True if format is valid
        """
        return self.extract_username(filename) is not None
    
    def get_debug_info(self, file_path: str) -> dict:
        """
        Get detailed debug information about username extraction
        
        Args:
            file_path (str): Full path to the file
            
        Returns:
            dict: Debug information
        """
        try:
            filename = Path(file_path).name
            name_without_ext = Path(filename).stem
            
            # Find digit blocks
            digit_blocks = []
            temp_name = name_without_ext
            
            while True:
                match = re.search(r'_(\d+)$', temp_name)
                if not match:
                    break
                digit_blocks.append(match.group(1))
                temp_name = temp_name[:match.start()]
            
            username_candidate = temp_name
            cleaned_username = self._clean_username(username_candidate)
            final_username = cleaned_username if self._is_valid_username(cleaned_username) else None
            
            return {
                'filename': filename,
                'name_without_ext': name_without_ext,
                'digit_blocks': digit_blocks,
                'username_candidate': username_candidate,
                'cleaned_username': cleaned_username,
                'final_username': final_username,
                'is_valid': final_username is not None
            }
            
        except Exception as e:
            return {'error': str(e)}