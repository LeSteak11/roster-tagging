"""
Validate migration results
"""

from database.db_manager import DatabaseManager

def validate_results():
    db = DatabaseManager()
    
    print("🎉 USERNAME MIGRATION - VALIDATION RESULTS")
    print("=" * 50)
    
    # Get stats
    total_profiles = db.get_profile_count()
    total_images = db.get_image_count()
    tagged_images = db.get_tagged_image_count()
    
    print(f"📊 Final Database Stats:")
    print(f"   • Total Profiles: {total_profiles}")
    print(f"   • Total Images: {total_images}")
    print(f"   • Tagged Images: {tagged_images}")
    print()
    
    # Get top profiles by image count
    profiles = db.get_profiles_with_counts()
    top_profiles = sorted(profiles, key=lambda x: x['image_count'], reverse=True)[:15]
    
    print(f"👥 Top 15 Profiles by Image Count:")
    for i, profile in enumerate(top_profiles, 1):
        print(f"   {i:2}. '{profile['username']}': {profile['image_count']} images")
    print()
    
    # Check for the specific examples mentioned
    examples = ['__ashleesparer__', '3masssy', '1reallykash']
    print(f"🔍 Checking specific examples:")
    for example in examples:
        images = db.get_images_by_username(example)
        if images:
            print(f"   ✅ '{example}': {len(images)} images")
            # Show a sample filename
            if images:
                print(f"      Sample: {images[0]['filename']}")
        else:
            print(f"   ❌ '{example}': Not found")
    print()
    
    # Check consolidation success
    single_image_profiles = sum(1 for p in profiles if p['image_count'] == 1)
    multi_image_profiles = sum(1 for p in profiles if p['image_count'] > 1)
    
    print(f"📈 Profile Consolidation Analysis:")
    print(f"   • Single-image profiles: {single_image_profiles}")
    print(f"   • Multi-image profiles: {multi_image_profiles}")
    print(f"   • Average images per profile: {total_images / total_profiles:.1f}")
    
    if total_profiles < 2000:  # Much fewer than the original 3219
        print(f"   ✅ Successfully consolidated profiles!")
    else:
        print(f"   ⚠️  Consolidation may not have worked as expected")

if __name__ == "__main__":
    validate_results()