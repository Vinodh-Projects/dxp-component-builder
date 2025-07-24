from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import logging
from openai import AsyncOpenAI
from anthropic import AsyncAnthropic
import json

from app.config import settings
from app.utils.cache import CacheManager
from app.utils.retry import retry_async

class BaseAgent(ABC):
    """Base class for all AI agents"""
    
    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(f"agent.{name}")
        self.cache = CacheManager()
        
        # Initialize AI clients
        self.openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.anthropic_client = None
        if settings.ANTHROPIC_API_KEY:
            self.anthropic_client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
    
    @abstractmethod
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input and return result"""
        pass
    
    @retry_async(max_attempts=3, delay=1.0)
    async def call_gpt4(self, prompt: str, model: str = None, **kwargs) -> str:
        """Call GPT-4 with retry logic"""
        model = model or settings.GPT4_MODEL
        
        response = await self.openai_client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": self.get_system_prompt()},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            **kwargs
        )
        
        return response.choices[0].message.content
    
    @retry_async(max_attempts=3, delay=1.0)
    async def call_gpt4_vision(self, prompt: str, image_url: str) -> str:
        """Call GPT-4 Vision for image analysis"""
        response = await self.openai_client.chat.completions.create(
            model=settings.GPT4_VISION_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": image_url}}
                    ]
                }
            ],
            max_tokens=4096
        )
        
        return response.choices[0].message.content
    
    @retry_async(max_attempts=3, delay=1.0)
    async def call_claude(self, prompt: str) -> str:
        """Call Claude for complex generation tasks"""
        if not self.anthropic_client:
            raise ValueError("Anthropic API key not configured")
        
        response = await self.anthropic_client.messages.create(
            model=settings.CLAUDE_MODEL,
            messages=[
                {"role": "user", "content": prompt}
            ],
            system=self.get_system_prompt(),
            max_tokens=8192
        )
        
        return response.content[0].text
    
    def parse_json_response(self, response: str) -> Dict[str, Any]:
        """Parse JSON from LLM response"""
        try:
            # Try to extract JSON from response
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            else:
                json_str = response.strip()
            
            return json.loads(json_str)
        except Exception as e:
            self.logger.error(f"Failed to parse JSON response: {e}")
            raise ValueError(f"Invalid JSON response: {e}")
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """Get the system prompt for this agent"""
        pass
