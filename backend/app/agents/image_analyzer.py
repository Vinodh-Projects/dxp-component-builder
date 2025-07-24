from typing import Dict, Any, Optional
from app.agents.base import BaseAgent

class ImageAnalyzer(BaseAgent):
    """Agent for analyzing component images and extracting code"""
    
    def __init__(self):
        super().__init__("image_analyzer")
    
    def get_system_prompt(self) -> str:
        return """You are an expert UI component analyzer. Extract the HTML structure, CSS styles, and JavaScript functionality from the provided image.

TASK: Analyze the component image and generate clean, semantic code.

EXTRACTION REQUIREMENTS:
1. HTML: Semantic structure with proper hierarchy
2. CSS: Modern, responsive styles with CSS variables
3. JavaScript: Vanilla JS for interactions (if any)

OUTPUT FORMAT (JSON only):
{
  "html": {
    "structure": "complete HTML structure",
    "semanticElements": ["list", "of", "elements"],
    "cssClasses": ["list", "of", "classes"]
  },
  "css": {
    "variables": {},
    "styles": "complete CSS",
    "responsive": {
      "breakpoints": ["768px", "1024px"],
      "mobileFirst": true
    }
  },
  "javascript": {
    "required": false,
    "functionality": [],
    "code": ""
  }
}"""    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze image and extract UI code"""
        
        image_url = input_data.get('image_url')
        if not image_url:
            return {
                "html": {"structure": "", "semanticElements": [], "cssClasses": []},
                "css": {"variables": {}, "styles": "", "responsive": {}},
                "javascript": {"required": False, "functionality": [], "code": ""}
            }
        
        # Check cache
        cache_key = f"img_analysis:{image_url}"
        cached_result = await self.cache.get(cache_key)
        if cached_result:
            return cached_result
        
        # Call GPT-4 Vision
        prompt = self.get_system_prompt() + f"\n\nAnalyze this component image and extract the code structure."
        response = await self.call_gpt4_vision(prompt, image_url)
        result = self.parse_json_response(response)
        
        # Cache result
        await self.cache.set(cache_key, result, ttl=7200)
        
        return result   