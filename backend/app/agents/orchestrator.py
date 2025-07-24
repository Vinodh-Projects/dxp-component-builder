from typing import Dict, Any, Optional
import asyncio
import uuid
from datetime import datetime
import logging

from app.agents.requirement_analyzer import RequirementAnalyzer
from app.agents.image_analyzer import ImageAnalyzer
from app.agents.component_generator import ComponentGenerator
from app.agents.validator import ComponentValidator
from app.utils.queue import TaskQueue
from app.models.responses import ComponentFiles, ValidationResult

class AgentOrchestrator:
    """Orchestrates the multi-agent workflow for component generation"""
    
    def __init__(self):
        self.logger = logging.getLogger("orchestrator")
        self.agents = {
            "requirement": RequirementAnalyzer(),
            "image": ImageAnalyzer(),
            "generator": ComponentGenerator(),
            "validator": ComponentValidator()
        }
        self.task_queue = TaskQueue()
        self.active_requests = {}
    
    async def initialize(self):
        """Initialize orchestrator and agents"""
        self.logger.info("Initializing Agent Orchestrator")
        await self.task_queue.initialize()
    
    async def cleanup(self):
        """Cleanup resources"""
        await self.task_queue.cleanup()
    
    async def generate_component(self, request_data: Dict[str, Any]) -> str:
        """Start component generation process"""
        
        request_id = str(uuid.uuid4())
        
        # Create task
        task = {
            "request_id": request_id,
            "request_data": request_data,
            "status": "queued",
            "created_at": datetime.utcnow().isoformat()
        }
        
        # Add to queue
        await self.task_queue.enqueue(task)
        
        # Start processing in background
        asyncio.create_task(self._process_request(request_id, request_data))
        
        return request_id
    
    async def get_status(self, request_id: str) -> Dict[str, Any]:
        """Get generation status"""
        
        status = await self.task_queue.get_status(request_id)
        if not status:
            raise ValueError(f"Request {request_id} not found")
        
        return status
    
    async def _process_request(self, request_id: str, request_data: Dict[str, Any]):
        """Process component generation request"""
        
        try:
            # Update status
            await self._update_status(request_id, "processing", 10, "Analyzing requirements")
            
            # Step 1: Analyze requirements
            requirements = await self.agents["requirement"].process({
                "description": request_data.get("description"),
                "fields": request_data.get("fields"),
                "component_type": request_data.get("component_type")
            })
            
            await self._update_status(request_id, "processing", 30, "Analyzing image")
            
            # Step 2: Analyze image (if provided)
            extracted_code = {}
            if request_data.get("image_url"):
                extracted_code = await self.agents["image"].process({
                    "image_url": request_data.get("image_url")
                })
            
            await self._update_status(request_id, "processing", 50, "Generating component")
            
            # Step 3: Generate component
            generated_files = await self.agents["generator"].process({
                "requirements": requirements,
                "extracted_code": extracted_code,
                "options": request_data.get("options", {})
            })
            
            await self._update_status(request_id, "processing", 80, "Validating component")
            
            # Step 4: Validate component
            validation_result = None
            if request_data.get("options", {}).get("validate", True):
                validation_result = await self.agents["validator"].process({
                    "files": generated_files
                })
            
            # Map keys to match ComponentFiles model
            mapped_files = self._map_file_keys(generated_files)
            
            # Map validation result keys if validation was performed
            mapped_validation = None
            if validation_result:
                mapped_validation = self._map_validation_keys(validation_result)
            
            # Prepare final result
            result = {
                "request_id": request_id,
                "status": "completed",
                "component_name": requirements.get("componentMetadata", {}).get("name"),
                "component_type": requirements.get("componentMetadata", {}).get("type", "custom"),
                "files": ComponentFiles(**mapped_files).dict(),
                "validation": ValidationResult(**mapped_validation).dict() if mapped_validation else None,
                "metadata": {
                    "requirements": requirements,
                    "extracted_code": extracted_code,
                    "generation_time": datetime.utcnow().isoformat()
                },
                "created_at": datetime.utcnow().isoformat()
            }
            
            # Save result
            await self.task_queue.save_result(request_id, result)
            await self._update_status(request_id, "completed", 100, "Generation complete")
            
        except Exception as e:
            self.logger.error(f"Error processing request {request_id}: {e}")
            await self._update_status(request_id, "failed", 0, str(e))
            raise
    
    async def _update_status(self, request_id: str, status: str, progress: int, message: str):
        """Update request status"""
        
        await self.task_queue.update_status(request_id, {
            "status": status,
            "progress": progress,
            "current_step": message,
            "updated_at": datetime.utcnow().isoformat()
        })
    
    def _map_file_keys(self, generated_files: Dict[str, Any]) -> Dict[str, Any]:
        """Map file keys from generator format to ComponentFiles model format"""
        
        key_mapping = {
            "slingModel": "sling_model",
            "htl": "htl",
            "dialog": "dialog",
            "contentXml": "content_xml",
            "clientlibs": "clientlibs"
        }
        
        mapped_files = {}
        for old_key, new_key in key_mapping.items():
            if old_key in generated_files:
                mapped_files[new_key] = generated_files[old_key]
            else:
                # Provide defaults for required fields
                if new_key in ["sling_model", "htl", "dialog", "content_xml"]:
                    mapped_files[new_key] = ""
                elif new_key == "clientlibs":
                    mapped_files[new_key] = {}
        
        # Always provide optional fields even if not in mapping
        mapped_files["sling_model_impl"] = None
        mapped_files["junit"] = None
        
        return mapped_files
    
    def _map_validation_keys(self, validation_result: Dict[str, Any]) -> Dict[str, Any]:
        """Map validation keys from validator format to ValidationResult model format"""
        
        key_mapping = {
            "validationStatus": "status",
            "score": "score", 
            "issues": "issues",
            "suggestions": "suggestions"
        }
        
        mapped_validation = {}
        for old_key, new_key in key_mapping.items():
            if old_key in validation_result:
                mapped_validation[new_key] = validation_result[old_key]
            else:
                # Provide defaults for required fields
                if new_key == "status":
                    mapped_validation[new_key] = "UNKNOWN"
                elif new_key == "score":
                    mapped_validation[new_key] = 0
                elif new_key in ["issues", "suggestions"]:
                    mapped_validation[new_key] = []
        
        return mapped_validation