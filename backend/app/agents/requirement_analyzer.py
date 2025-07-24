from typing import Dict, Any, List
from app.agents.base import BaseAgent
from app.models.requests import ComponentField, FieldType

class RequirementAnalyzer(BaseAgent):
    """Agent for analyzing user requirements and extracting component details"""
    
    def __init__(self):
        super().__init__("requirement_analyzer")
    
    def get_system_prompt(self) -> str:
        return """You are an AEM Component Requirements Analyzer. Extract and structure component requirements from user input.

TASK: Analyze the user's request and extract all component details into a structured format.

INPUT ANALYSIS:
- Component name and type
- Required fields/properties with their types
- Visual/functional requirements
- Any specific constraints or features

OUTPUT FORMAT (JSON only):
{
  "componentMetadata": {
    "name": "component-name",
    "displayName": "Component Display Name",
    "group": "Component.Group",
    "description": "Component description"
  },
  "fields": [
    {
      "name": "fieldName",
      "label": "Field Label",
      "type": "fieldType",
      "required": true/false,
      "description": "Field description",
      "validation": {}
    }
  ],
  "features": {
    "responsive": true,
    "accessibility": true,
    "lazyLoading": true,
    "animations": false
  }
}"""
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze user requirements and extract component details"""
        
        # Check cache first
        cache_key = f"req_analysis:{input_data['description']}"
        cached_result = await self.cache.get(cache_key)
        if cached_result:
            return cached_result
        
        # Build prompt
        prompt = f"User Request: {input_data['description']}"
        
        # Add any provided fields to the prompt
        if input_data.get('fields'):
            prompt += f"\n\nProvided fields: {input_data['fields']}"
        
        # Call LLM
        response = await self.call_gpt4(prompt)
        result = self.parse_json_response(response)
        
        # Cache result
        await self.cache.set(cache_key, result, ttl=3600)
        
        return result
