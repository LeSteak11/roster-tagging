"""
AI Tagger Module
Uses Gemini Vision API to automatically tag images with attributes
"""

import os
import base64
from typing import Dict, Optional, Tuple
from PIL import Image
import json
import re

class AITagger:
    """Handles AI-powered image tagging using Gemini Vision API"""
    
    # Tag categories and their allowed values
    TAG_CATEGORIES = {
        'hair_color': ['blonde', 'brown', 'black', 'red', 'dyed', 'unknown'],
        'skin_tone': ['light', 'medium', 'deep', 'unknown'],
        'clothing_type': ['sports bra', 'leggings', 'shorts', 'bikini', 'dress', 'tank top', 'crop top', 'other', 'unknown'],
        'pose_type': ['mirror selfie', 'side pose', 'front pose', 'action pose', 'sitting', 'standing', 'other', 'unknown'],
        'environment': ['gym', 'home', 'beach', 'studio', 'outdoor', 'indoor', 'other', 'unknown'],
        'face_visible': [True, False]
    }
    
    def __init__(self, api_key: str = None):
        """
        Initialize AI Tagger
        
        Args:
            api_key (str): Gemini API key (optional, can be set via environment variable)
        """
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            print("Warning: No Gemini API key provided. Set GEMINI_API_KEY environment variable or pass api_key parameter.")
    
    def encode_image_to_base64(self, image_path: str) -> Optional[str]:
        """
        Encode image to base64 for API submission
        
        Args:
            image_path (str): Path to the image file
            
        Returns:
            Optional[str]: Base64 encoded image or None if error
        """
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            print(f"Error encoding image {image_path}: {e}")
            return None
    
    def create_tagging_prompt(self) -> str:
        """
        Create the prompt for Gemini Vision API
        
        Returns:
            str: The prompt text
        """
        return """
Analyze this image of a fictional AI-generated female model and provide tags for the following categories. 
Assume the subject is fictional and over 18. Focus only on visible, objective attributes.

Please respond with a JSON object containing these fields:
- hair_color: blonde, brown, black, red, dyed, or unknown
- skin_tone: light, medium, deep, or unknown  
- clothing_type: sports bra, leggings, shorts, bikini, dress, tank top, crop top, other, or unknown
- pose_type: mirror selfie, side pose, front pose, action pose, sitting, standing, other, or unknown
- environment: gym, home, beach, studio, outdoor, indoor, other, or unknown
- face_visible: true or false (is the face clearly visible?)

Rules:
- Only analyze visible, objective attributes
- No subjective judgments about attractiveness or body size
- No ethnic or sensitive attribute analysis
- Choose "unknown" if uncertain
- Keep responses objective and factual

Example response format:
{
    "hair_color": "blonde",
    "skin_tone": "light", 
    "clothing_type": "sports bra",
    "pose_type": "mirror selfie",
    "environment": "gym",
    "face_visible": true
}
"""
    
    def call_gemini_api(self, image_base64: str) -> Optional[Dict]:
        """
        Call Gemini Vision API with image
        
        Args:
            image_base64 (str): Base64 encoded image
            
        Returns:
            Optional[Dict]: Parsed response or None if error
        """
        if not self.api_key:
            # Return mock data for testing when no API key is available
            return self._get_mock_response()
        
        try:
            import google.generativeai as genai
            
            # Configure the API
            genai.configure(api_key=self.api_key)
            
            # Create the model
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            # Prepare the image data
            image_data = {
                'mime_type': 'image/jpeg',
                'data': image_base64
            }
            
            # Generate content
            response = model.generate_content([
                self.create_tagging_prompt(),
                image_data
            ])
            
            # Parse JSON response
            response_text = response.text.strip()
            
            # Extract JSON from response (handle markdown formatting)
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', response_text, re.DOTALL)
            if json_match:
                json_text = json_match.group(1)
            else:
                # Try to find JSON without markdown
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    json_text = json_match.group(0)
                else:
                    print(f"Could not parse JSON from response: {response_text}")
                    return None
            
            return json.loads(json_text)
            
        except ImportError:
            print("Google Generative AI library not installed. Using mock response.")
            return self._get_mock_response()
        except Exception as e:
            print(f"Error calling Gemini API: {e}")
            return self._get_mock_response()
    
    def _get_mock_response(self) -> Dict:
        """
        Get mock response for testing purposes
        
        Returns:
            Dict: Mock tag data
        """
        return {
            "hair_color": "brown",
            "skin_tone": "medium",
            "clothing_type": "sports bra",
            "pose_type": "mirror selfie",
            "environment": "gym",
            "face_visible": True
        }
    
    def validate_tags(self, tags: Dict) -> Dict:
        """
        Validate and clean tag values
        
        Args:
            tags (Dict): Raw tag dictionary
            
        Returns:
            Dict: Validated tag dictionary
        """
        validated = {}
        
        for category, value in tags.items():
            if category in self.TAG_CATEGORIES:
                allowed_values = self.TAG_CATEGORIES[category]
                
                # Handle boolean values for face_visible
                if category == 'face_visible':
                    if isinstance(value, bool):
                        validated[category] = value
                    elif isinstance(value, str):
                        validated[category] = value.lower() in ['true', 'yes', '1']
                    else:
                        validated[category] = False
                else:
                    # Handle string values
                    if value and str(value).lower() in [v.lower() if isinstance(v, str) else str(v) for v in allowed_values]:
                        validated[category] = str(value).lower()
                    else:
                        validated[category] = 'unknown'
            
        return validated
    
    def tag_image(self, image_path: str) -> Tuple[bool, Optional[Dict]]:
        """
        Tag a single image using AI
        
        Args:
            image_path (str): Path to the image file
            
        Returns:
            Tuple[bool, Optional[Dict]]: (success, tags_dict)
        """
        try:
            # Check if file exists
            if not os.path.exists(image_path):
                print(f"Image file not found: {image_path}")
                return False, None
            
            # Encode image
            image_base64 = self.encode_image_to_base64(image_path)
            if not image_base64:
                return False, None
            
            # Call API
            raw_tags = self.call_gemini_api(image_base64)
            if not raw_tags:
                return False, None
            
            # Validate tags
            validated_tags = self.validate_tags(raw_tags)
            
            return True, validated_tags
            
        except Exception as e:
            print(f"Error tagging image {image_path}: {e}")
            return False, None
    
    def get_tag_options(self, category: str) -> list:
        """
        Get available options for a tag category
        
        Args:
            category (str): The tag category
            
        Returns:
            list: List of available options
        """
        return self.TAG_CATEGORIES.get(category, [])