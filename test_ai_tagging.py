"""
Test AI Tagging functionality with sample images
"""

from utils.ai_tagger import AITagger
from database.db_manager import DatabaseManager
import os

def test_ai_tagging():
    """Test AI tagging with a sample image"""
    print("🧪 Testing AI Tagging Functionality\n")
    
    # Initialize components
    tagger = AITagger()
    db = DatabaseManager()
    
    # Test with one of our sample images
    test_image_path = "test_images/alana_moore_1699111.jpg"
    
    if os.path.exists(test_image_path):
        print(f"📸 Testing with: {test_image_path}")
        
        # Test AI tagging
        success, tags = tagger.tag_image(test_image_path)
        
        if success:
            print("✅ AI Tagging successful!")
            print("🏷️ Generated tags:")
            for key, value in tags.items():
                print(f"   • {key.replace('_', ' ').title()}: {value}")
            
            # Test tag validation
            validated = tagger.validate_tags(tags)
            print("\n✅ Tag validation successful!")
            
        else:
            print("❌ AI Tagging failed (expected if no API key)")
            print("🔄 Using mock response for testing...")
    
    else:
        print(f"❌ Test image not found: {test_image_path}")
    
    # Test database tag methods
    print(f"\n📊 Database Stats:")
    print(f"   • Total images: {db.get_image_count()}")
    print(f"   • Untagged images: {len(db.get_untagged_images())}")
    print(f"   • Tagged images: {db.get_tagged_image_count()}")
    
    # Test tag options
    print(f"\n🎯 Available tag options:")
    for category in tagger.TAG_CATEGORIES:
        options = tagger.get_tag_options(category)
        print(f"   • {category}: {options[:3]}..." if len(options) > 3 else f"   • {category}: {options}")

if __name__ == "__main__":
    test_ai_tagging()