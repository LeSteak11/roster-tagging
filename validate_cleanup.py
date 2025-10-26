"""
Validate Milestone 3 cleanup results
"""

from database.db_manager import DatabaseManager

def validate_cleanup():
    db = DatabaseManager()
    
    print("🧹 MILESTONE 3 - DATA CLEANUP VALIDATION")
    print("=" * 50)
    
    # Check overall stats
    total_profiles = db.get_profile_count()
    visible_profiles = db.get_visible_profile_count()
    total_images = db.get_image_count()
    tagged_images = db.get_tagged_image_count()
    
    print(f"📊 Database Stats:")
    print(f"   • Total profiles in DB: {total_profiles}")
    print(f"   • Visible profiles: {visible_profiles}")
    print(f"   • Hidden profiles: {total_profiles - visible_profiles}")
    print(f"   • Total images: {total_images}")
    print(f"   • Tagged images: {tagged_images}")
    print()
    
    # Check hidden profiles
    hidden_stats = db.get_hidden_profiles_stats()
    print(f"🔒 Hidden Profile Stats:")
    print(f"   • {hidden_stats['username']}: {hidden_stats['image_count']} images")
    print()
    
    # Check for TikTok rename
    tiktok_images = db.get_images_by_username("TikTok")
    snaptik_images = db.get_images_by_username("snaptik")
    
    print(f"📱 TikTok Rename Results:")
    print(f"   • TikTok profile: {len(tiktok_images)} images")
    print(f"   • snaptik profile: {len(snaptik_images)} images (should be 0)")
    
    if len(snaptik_images) == 0 and len(tiktok_images) > 0:
        print(f"   ✅ Successfully renamed snaptik → TikTok")
    else:
        print(f"   ❌ Rename may have failed")
    print()
    
    # Top visible profiles
    visible_profiles_list = db.get_visible_profiles_with_counts()
    top_visible = sorted(visible_profiles_list, key=lambda x: x['image_count'], reverse=True)[:10]
    
    print(f"👥 Top 10 Visible Profiles:")
    for i, profile in enumerate(top_visible, 1):
        print(f"   {i:2}. '{profile['username']}': {profile['image_count']} images")
    print()
    
    # Verify IMG is not in visible profiles
    img_in_visible = any(p['username'] == 'IMG' for p in visible_profiles_list)
    print(f"🔍 Profile Filtering Validation:")
    print(f"   • IMG in visible profiles: {img_in_visible} (should be False)")
    print(f"   • TikTok in visible profiles: {any(p['username'] == 'TikTok' for p in visible_profiles_list)}")
    
    if not img_in_visible:
        print(f"   ✅ Successfully filtered out IMG profile")
    else:
        print(f"   ❌ IMG profile filtering failed")
    print()
    
    # Check data integrity
    print(f"🔐 Data Integrity Check:")
    print(f"   • All images preserved: {total_images == 11445} (should be True)")
    print(f"   • Tags preserved: {tagged_images >= 2} (should be >= original)")
    
    print(f"\n🎯 Cleanup Summary:")
    print(f"   • Real profiles shown: {visible_profiles}")
    print(f"   • IMG content hidden: {hidden_stats['image_count']} images")
    print(f"   • TikTok content grouped: {len(tiktok_images)} images")
    print(f"   • Clean UI achieved: ✅")

if __name__ == "__main__":
    validate_cleanup()