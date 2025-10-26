"""
Data Migration Script
Recompute usernames for all existing images and update the database
"""

from database.db_manager import DatabaseManager
from utils.username_extractor import UsernameExtractor
import sqlite3
from datetime import datetime
from collections import defaultdict

class DataMigrator:
    """Handles migration of existing data to new username format"""
    
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.extractor = UsernameExtractor()
        self.migration_stats = {
            'total_images': 0,
            'successfully_parsed': 0,
            'failed_parsing': 0,
            'profiles_before': 0,
            'profiles_after': 0,
            'profiles_merged': 0
        }
    
    def backup_database(self):
        """Create a backup of the current database"""
        backup_name = f"roster_tagging_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        
        try:
            with sqlite3.connect(self.db_manager.db_path) as source:
                with sqlite3.connect(backup_name) as backup:
                    source.backup(backup)
            print(f"✅ Database backed up to: {backup_name}")
            return backup_name
        except Exception as e:
            print(f"❌ Backup failed: {e}")
            return None
    
    def analyze_current_data(self):
        """Analyze current data to understand the migration scope"""
        print("🔍 Analyzing current data...\n")
        
        # Get current stats
        self.migration_stats['profiles_before'] = self.db_manager.get_profile_count()
        self.migration_stats['total_images'] = self.db_manager.get_image_count()
        
        print(f"📊 Current Database:")
        print(f"   • Profiles: {self.migration_stats['profiles_before']}")
        print(f"   • Images: {self.migration_stats['total_images']}")
        
        # Sample some filenames to show the issue
        with sqlite3.connect(self.db_manager.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT filename, username FROM images LIMIT 10")
            samples = cursor.fetchall()
        
        print(f"\n🔍 Sample current usernames (showing parsing issues):")
        username_changes = defaultdict(list)
        
        for sample in samples:
            old_username = sample['username']
            new_username = self.extractor.extract_username(sample['filename'])
            
            if new_username and new_username != old_username:
                username_changes[new_username].append(old_username)
            
            print(f"   File: {sample['filename']}")
            print(f"   Old:  '{old_username}' → New: '{new_username}'")
            print()
        
        if username_changes:
            print("👥 Profile consolidation preview:")
            for new_name, old_names in list(username_changes.items())[:5]:
                print(f"   '{new_name}' will merge: {old_names}")
        
        return username_changes
    
    def migrate_usernames(self, dry_run=True):
        """
        Migrate all usernames to the new format
        
        Args:
            dry_run (bool): If True, only show what would be changed
        """
        print(f"\n{'🔍 DRY RUN' if dry_run else '🚀 MIGRATING'} - Recomputing usernames...\n")
        
        # Get all images
        with sqlite3.connect(self.db_manager.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT id, filename, filepath, username FROM images")
            all_images = cursor.fetchall()
        
        # Track changes
        username_mapping = {}  # old_username -> new_username
        image_updates = []     # (image_id, new_username)
        new_profile_groups = defaultdict(list)  # new_username -> [image_ids]
        
        for image in all_images:
            old_username = image['username']
            new_username = self.extractor.extract_username(image['filename'])
            
            if new_username:
                self.migration_stats['successfully_parsed'] += 1
                
                # Track the mapping
                if old_username != new_username:
                    username_mapping[old_username] = new_username
                
                # Record this image for update
                image_updates.append((image['id'], new_username))
                new_profile_groups[new_username].append(image['id'])
            else:
                self.migration_stats['failed_parsing'] += 1
                print(f"⚠️  Failed to parse: {image['filename']}")
        
        print(f"📊 Migration Analysis:")
        print(f"   • Successfully parsed: {self.migration_stats['successfully_parsed']}")
        print(f"   • Failed parsing: {self.migration_stats['failed_parsing']}")
        print(f"   • Unique new profiles: {len(new_profile_groups)}")
        
        # Show consolidation stats
        consolidations = []
        for new_username, image_ids in new_profile_groups.items():
            if len(image_ids) > 1:
                # Get the old usernames for these images
                old_usernames = set()
                for image in all_images:
                    if image['id'] in image_ids:
                        old_usernames.add(image['username'])
                
                if len(old_usernames) > 1:
                    consolidations.append((new_username, len(old_usernames), len(image_ids)))
        
        if consolidations:
            print(f"\n👥 Profile Consolidations (top 10):")
            for new_name, old_count, image_count in sorted(consolidations, key=lambda x: x[2], reverse=True)[:10]:
                print(f"   • '{new_name}': {old_count} profiles → {image_count} images")
        
        if not dry_run:
            self._perform_migration(image_updates, new_profile_groups)
        
        return username_mapping, new_profile_groups
    
    def _perform_migration(self, image_updates, new_profile_groups):
        """Actually perform the database migration"""
        print(f"\n🔄 Performing database migration...")
        
        try:
            with sqlite3.connect(self.db_manager.db_path) as conn:
                cursor = conn.cursor()
                
                # Step 1: Create new profiles
                print("   • Creating new profiles...")
                for new_username in new_profile_groups.keys():
                    cursor.execute("INSERT OR IGNORE INTO profiles (username) VALUES (?)", (new_username,))
                
                # Step 2: Update all images with new usernames
                print("   • Updating image usernames...")
                for image_id, new_username in image_updates:
                    cursor.execute("UPDATE images SET username = ? WHERE id = ?", (new_username, image_id))
                
                # Step 3: Clean up orphaned profiles (profiles with no images)
                print("   • Cleaning up orphaned profiles...")
                cursor.execute("""
                DELETE FROM profiles 
                WHERE username NOT IN (SELECT DISTINCT username FROM images)
                """)
                
                conn.commit()
                
                # Update stats
                cursor.execute("SELECT COUNT(*) FROM profiles")
                self.migration_stats['profiles_after'] = cursor.fetchone()[0]
                
                self.migration_stats['profiles_merged'] = (
                    self.migration_stats['profiles_before'] - self.migration_stats['profiles_after']
                )
                
            print("✅ Migration completed successfully!")
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            raise
    
    def validate_migration(self):
        """Validate the migration results"""
        print(f"\n✅ Migration Validation:")
        print(f"   • Profiles before: {self.migration_stats['profiles_before']}")
        print(f"   • Profiles after:  {self.migration_stats['profiles_after']}")
        print(f"   • Profiles merged: {self.migration_stats['profiles_merged']}")
        print(f"   • Images processed: {self.migration_stats['successfully_parsed']}")
        print(f"   • Parse failures: {self.migration_stats['failed_parsing']}")
        
        # Test a few random samples
        profiles = self.db_manager.get_profiles_with_counts()
        if profiles:
            print(f"\n📋 Sample updated profiles:")
            for profile in profiles[:5]:
                print(f"   • '{profile['username']}': {profile['image_count']} images")
    
    def run_full_migration(self, force=False):
        """Run the complete migration process"""
        print("🔄 ROSTER TAGGING - USERNAME MIGRATION")
        print("=" * 50)
        
        # Step 1: Backup
        backup_file = self.backup_database()
        if not backup_file and not force:
            print("❌ Cannot proceed without backup. Use force=True to override.")
            return False
        
        # Step 2: Analyze
        self.analyze_current_data()
        
        # Step 3: Dry run
        print("\n" + "=" * 50)
        self.migrate_usernames(dry_run=True)
        
        # Step 4: Confirm
        if not force:
            confirm = input(f"\n⚠️  Proceed with migration? This will update {self.migration_stats['total_images']} images. (y/N): ")
            if confirm.lower() != 'y':
                print("❌ Migration cancelled.")
                return False
        
        # Step 5: Migrate
        print("\n" + "=" * 50)
        self.migrate_usernames(dry_run=False)
        
        # Step 6: Validate
        self.validate_migration()
        
        print(f"\n🎉 Migration completed! Backup saved as: {backup_file}")
        return True

def main():
    """Run the migration script"""
    migrator = DataMigrator()
    
    # Run with confirmation
    migrator.run_full_migration(force=False)

if __name__ == "__main__":
    main()