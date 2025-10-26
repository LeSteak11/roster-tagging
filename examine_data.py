"""
Quick script to examine database contents
"""

from database.db_manager import DatabaseManager
import sqlite3

def examine_data():
    db = DatabaseManager()
    
    with sqlite3.connect(db.db_path) as conn:
        cursor = conn.cursor()
        
        # Look for complex filenames
        cursor.execute("""
        SELECT filename, username 
        FROM images 
        WHERE filename LIKE '%ashlee%' 
           OR filename LIKE '%masssy%'
           OR filename LIKE '%____%'
           OR length(filename) - length(replace(filename, '_', '')) > 3
        LIMIT 10
        """)
        
        samples = cursor.fetchall()
        
        print("🔍 Complex filenames found:")
        for filename, username in samples:
            print(f"   File: {filename}")
            print(f"   Current Username: '{username}'")
            print()
        
        # Get some stats
        cursor.execute("SELECT COUNT(DISTINCT username) as profile_count FROM images")
        profile_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) as image_count FROM images")
        image_count = cursor.fetchone()[0]
        
        print(f"📊 Current Stats:")
        print(f"   Profiles: {profile_count}")
        print(f"   Images: {image_count}")

if __name__ == "__main__":
    examine_data()