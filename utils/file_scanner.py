"""
File Scanner Module
Scans folders for supported image and video files
"""

import os
from pathlib import Path
from typing import List

class FileScanner:
    """Handles scanning directories for supported media files"""
    
    SUPPORTED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.mp4'}
    
    def __init__(self):
        pass
    
    def scan_folder(self, folder_path: str) -> List[str]:
        """
        Scan a folder for supported image and video files
        
        Args:
            folder_path (str): Path to the folder to scan
            
        Returns:
            List[str]: List of file paths found
        """
        found_files = []
        
        try:
            folder = Path(folder_path)
            if not folder.exists() or not folder.is_dir():
                return found_files
            
            # Recursively scan folder
            for file_path in folder.rglob('*'):
                if file_path.is_file():
                    if file_path.suffix.lower() in self.SUPPORTED_EXTENSIONS:
                        found_files.append(str(file_path))
            
            return found_files
            
        except Exception as e:
            print(f"Error scanning folder {folder_path}: {e}")
            return found_files
    
    def is_supported_file(self, file_path: str) -> bool:
        """
        Check if a file has a supported extension
        
        Args:
            file_path (str): Path to the file
            
        Returns:
            bool: True if file is supported
        """
        return Path(file_path).suffix.lower() in self.SUPPORTED_EXTENSIONS