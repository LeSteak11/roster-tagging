"""
Database Manager Module
Handles SQLite database operations for Roster Tagging application
"""

import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path

class DatabaseManager:
    """Manages SQLite database operations"""
    
    def __init__(self, db_path: str = "roster_tagging.db"):
        """
        Initialize database manager
        
        Args:
            db_path (str): Path to SQLite database file
        """
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database and create tables if they don't exist"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create Profiles table
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS profiles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL
                )
                """)
                
                # Create Images table
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS images (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filename TEXT NOT NULL,
                    filepath TEXT NOT NULL,
                    username TEXT NOT NULL,
                    date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (username) REFERENCES profiles (username)
                )
                """)
                
                # Create index for faster lookups
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_username ON images (username)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_filepath ON images (filepath)")
                
                conn.commit()
                
        except Exception as e:
            print(f"Error initializing database: {e}")
    
    def add_profile(self, username: str) -> bool:
        """
        Add a new profile or ignore if already exists
        
        Args:
            username (str): The username to add
            
        Returns:
            bool: True if successful
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT OR IGNORE INTO profiles (username) VALUES (?)", (username,))
                conn.commit()
                return True
        except Exception as e:
            print(f"Error adding profile {username}: {e}")
            return False
    
    def add_image(self, filename: str, filepath: str, username: str) -> bool:
        """
        Add a new image record
        
        Args:
            filename (str): Name of the image file
            filepath (str): Full path to the image file
            username (str): Username associated with the image
            
        Returns:
            bool: True if successful
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Check if image already exists (avoid duplicates)
                cursor.execute("SELECT id FROM images WHERE filepath = ?", (filepath,))
                if cursor.fetchone():
                    return True  # Already exists, consider it successful
                
                # Add the image
                cursor.execute("""
                INSERT INTO images (filename, filepath, username, date_added)
                VALUES (?, ?, ?, ?)
                """, (filename, filepath, username, datetime.now()))
                
                conn.commit()
                return True
        except Exception as e:
            print(f"Error adding image {filename}: {e}")
            return False
    
    def get_all_profiles(self) -> List[Dict]:
        """
        Get all profiles from database
        
        Returns:
            List[Dict]: List of profile dictionaries
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM profiles ORDER BY username")
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"Error getting profiles: {e}")
            return []
    
    def get_profiles_with_counts(self) -> List[Dict]:
        """
        Get all profiles with their image counts
        
        Returns:
            List[Dict]: List of profile dictionaries with image_count field
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("""
                SELECT p.id, p.username, COUNT(i.id) as image_count
                FROM profiles p
                LEFT JOIN images i ON p.username = i.username
                GROUP BY p.id, p.username
                ORDER BY p.username
                """)
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"Error getting profiles with counts: {e}")
            return []
    
    def get_images_by_username(self, username: str) -> List[Dict]:
        """
        Get all images for a specific username
        
        Args:
            username (str): The username to search for
            
        Returns:
            List[Dict]: List of image dictionaries
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM images WHERE username = ? ORDER BY date_added DESC", (username,))
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"Error getting images for {username}: {e}")
            return []
    
    def get_profile_count(self) -> int:
        """Get total number of profiles"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM profiles")
                return cursor.fetchone()[0]
        except Exception as e:
            print(f"Error getting profile count: {e}")
            return 0
    
    def get_image_count(self) -> int:
        """Get total number of images"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM images")
                return cursor.fetchone()[0]
        except Exception as e:
            print(f"Error getting image count: {e}")
            return 0
    
    def delete_profile(self, username: str) -> bool:
        """
        Delete a profile and all associated images
        
        Args:
            username (str): The username to delete
            
        Returns:
            bool: True if successful
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Delete associated images first
                cursor.execute("DELETE FROM images WHERE username = ?", (username,))
                
                # Delete the profile
                cursor.execute("DELETE FROM profiles WHERE username = ?", (username,))
                
                conn.commit()
                return True
        except Exception as e:
            print(f"Error deleting profile {username}: {e}")
            return False