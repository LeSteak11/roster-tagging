"""
Test the updated username extraction logic
"""

from utils.username_extractor import UsernameExtractor

def test_new_extraction():
    """Test the new username extraction with example cases"""
    extractor = UsernameExtractor()
    
    test_cases = [
        ("__ashleesparer___1754697541_3694993242088387086_3400365034.jpg", "__ashleesparer__"),
        ("3masssy_1632363949.jpg", "3masssy"),
        ("1reallykash_1630964335.jpg", "1reallykash"),
        ("alana_moore_3839299832.jpg", "alana_moore"),
        ("jessica_smith_1234567890.png", "jessica_smith"),
        ("maria_garcia_9876543210.mp4", "maria_garcia"),
        ("simple_123.jpg", "simple"),
        ("complex_name_with_underscores_999888777.jpg", "complex_name_with_underscores"),
        ("invalid_filename.jpg", None),  # No numbers
        ("123_456.jpg", None),  # Only numbers
    ]
    
    print("🧪 Testing Updated Username Extraction\n")
    
    for filename, expected in test_cases:
        result = extractor.extract_username(filename)
        status = "✅" if result == expected else "❌"
        print(f"{status} {filename}")
        print(f"   Expected: {expected}")
        print(f"   Got:      {result}")
        
        # Show debug info for failed cases
        if result != expected:
            debug = extractor.get_debug_info(filename)
            print(f"   Debug:    {debug}")
        print()

if __name__ == "__main__":
    test_new_extraction()