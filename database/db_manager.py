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
                
                # Create Tags table
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS tags (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    image_id INTEGER NOT NULL,
                    hair_color TEXT,
                    skin_tone TEXT,
                    clothing_type TEXT,
                    pose_type TEXT,
                    environment TEXT,
                    face_visible BOOLEAN,
                    date_tagged TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (image_id) REFERENCES images (id) ON DELETE CASCADE
                )
                """)
                
                # Create index for faster lookups
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_username ON images (username)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_filepath ON images (filepath)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_image_id ON tags (image_id)")
                
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
    
    def add_tags(self, image_id: int, hair_color: str = None, skin_tone: str = None, 
                 clothing_type: str = None, pose_type: str = None, environment: str = None, 
                 face_visible: bool = None) -> bool:
        """
        Add or update tags for an image
        
        Args:
            image_id (int): The image ID to tag
            hair_color (str): Hair color tag
            skin_tone (str): Skin tone tag
            clothing_type (str): Clothing type tag
            pose_type (str): Pose type tag
            environment (str): Environment tag
            face_visible (bool): Face visibility tag
            
        Returns:
            bool: True if successful
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Check if tags already exist for this image
                cursor.execute("SELECT id FROM tags WHERE image_id = ?", (image_id,))
                existing = cursor.fetchone()
                
                if existing:
                    # Update existing tags
                    cursor.execute("""
                    UPDATE tags SET 
                        hair_color = ?, skin_tone = ?, clothing_type = ?, 
                        pose_type = ?, environment = ?, face_visible = ?,
                        date_tagged = CURRENT_TIMESTAMP
                    WHERE image_id = ?
                    """, (hair_color, skin_tone, clothing_type, pose_type, 
                          environment, face_visible, image_id))
                else:
                    # Insert new tags
                    cursor.execute("""
                    INSERT INTO tags (image_id, hair_color, skin_tone, clothing_type, 
                                    pose_type, environment, face_visible)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (image_id, hair_color, skin_tone, clothing_type, 
                          pose_type, environment, face_visible))
                
                conn.commit()
                return True
        except Exception as e:
            print(f"Error adding tags for image {image_id}: {e}")
            return False
    
    def get_tags_by_image_id(self, image_id: int) -> Optional[Dict]:
        """
        Get tags for a specific image
        
        Args:
            image_id (int): The image ID
            
        Returns:
            Optional[Dict]: Tag dictionary or None if not found
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM tags WHERE image_id = ?", (image_id,))
                result = cursor.fetchone()
                return dict(result) if result else None
        except Exception as e:
            print(f"Error getting tags for image {image_id}: {e}")
            return None
    
    def get_untagged_images(self) -> List[Dict]:
        """
        Get all images that don't have tags yet
        
        Returns:
            List[Dict]: List of untagged image dictionaries
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("""
                SELECT i.* FROM images i
                LEFT JOIN tags t ON i.id = t.image_id
                WHERE t.image_id IS NULL
                ORDER BY i.date_added DESC
                """)
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"Error getting untagged images: {e}")
            return []
    
    def get_tagged_image_count(self) -> int:
        """Get count of images that have been tagged"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(DISTINCT image_id) FROM tags")
                return cursor.fetchone()[0]
        except Exception as e:
            print(f"Error getting tagged image count: {e}")
            return 0
    
    def get_visible_profiles_with_counts(self) -> List[Dict]:
        """
        Get all visible profiles (excluding hidden ones like IMG) with their image counts
        
        Returns:
            List[Dict]: List of visible profile dictionaries with image_count field
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("""
                SELECT p.id, p.username, COUNT(i.id) as image_count
                FROM profiles p
                LEFT JOIN images i ON p.username = i.username
                WHERE p.username != 'IMG'
                GROUP BY p.id, p.username
                HAVING COUNT(i.id) > 0
                ORDER BY p.username
                """)
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"Error getting visible profiles with counts: {e}")
            return []
    
    def get_hidden_profiles_stats(self) -> Dict:
        """
        Get statistics for hidden profiles
        
        Returns:
            Dict: Statistics for hidden profiles
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("""
                SELECT p.username, COUNT(i.id) as image_count
                FROM profiles p
                LEFT JOIN images i ON p.username = i.username
                WHERE p.username = 'IMG'
                GROUP BY p.username
                """)
                result = cursor.fetchone()
                
                if result:
                    return {
                        'username': result['username'],
                        'image_count': result['image_count']
                    }
                else:
                    return {'username': 'IMG', 'image_count': 0}
        except Exception as e:
            print(f"Error getting hidden profiles stats: {e}")
            return {'username': 'IMG', 'image_count': 0}
    
    def get_visible_profile_count(self) -> int:
        """Get count of visible profiles (excluding hidden ones)"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM profiles WHERE username != 'IMG'")
                return cursor.fetchone()[0]
        except Exception as e:
            print(f"Error getting visible profile count: {e}")
            return 0
    
    def rename_profile(self, old_username: str, new_username: str) -> bool:
        """
        Rename a profile and update all associated images
        
        Args:
            old_username (str): Current username
            new_username (str): New username
            
        Returns:
            bool: True if successful
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Check if new username already exists
                cursor.execute("SELECT id FROM profiles WHERE username = ?", (new_username,))
                existing = cursor.fetchone()
                
                if existing:
                    # New username exists, merge profiles
                    # Update all images to use new username
                    cursor.execute("UPDATE images SET username = ? WHERE username = ?", 
                                 (new_username, old_username))
                    # Delete old profile
                    cursor.execute("DELETE FROM profiles WHERE username = ?", (old_username,))
                else:
                    # New username doesn't exist, simple rename
                    cursor.execute("UPDATE profiles SET username = ? WHERE username = ?", 
                                 (new_username, old_username))
                    cursor.execute("UPDATE images SET username = ? WHERE username = ?", 
                                 (new_username, old_username))
                
                conn.commit()
                return True
        except Exception as e:
            print(f"Error renaming profile from {old_username} to {new_username}: {e}")
            return False