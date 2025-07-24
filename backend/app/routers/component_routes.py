from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, BackgroundTasks, Form
from fastapi.responses import JSONResponse
from typing import Optional, Dict, Any
import logging
import json

from app.models.requests import ComponentRequest, GenerationOptions
from app.models.responses import ComponentResponse, GenerationStatus
from app.utils.file_handler import FileHandler
from app.agents.orchestrator import AgentOrchestrator

router = APIRouter()
logger = logging.getLogger(__name__)

async def get_orchestrator() -> AgentOrchestrator:
    """Dependency to get orchestrator from app state"""
    from main import app
    return app.state.orchestrator

@router.post("/generate", response_model=Dict[str, str])
async def generate_component(
    request: ComponentRequest,
    image: Optional[UploadFile] = File(None),
    options: Optional[GenerationOptions] = None,
    orchestrator: AgentOrchestrator = Depends(get_orchestrator)
):
    """Generate AEM component from requirements"""
    
    try:
        # Handle image upload if provided
        image_url = None
        if image:
            file_handler = FileHandler()
            image_url = await file_handler.upload_image(image)
        
        # Prepare request data
        request_data = {
            "description": request.description,
            "component_type": request.component_type,
            "fields": [field.dict() for field in request.fields] if request.fields else None,
            "image_url": image_url,
            "project_namespace": request.project_namespace,
            "component_group": request.component_group,
            "options": options.dict() if options else GenerationOptions().dict()
        }
        
        # Start generation process
        request_id = await orchestrator.generate_component(request_data)
        
        return {
            "request_id": request_id,
            "message": "Component generation started",
            "status_url": f"/api/v1/components/status/{request_id}"
        }
        
    except Exception as e:
        logger.error(f"Error generating component: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-form", response_model=Dict[str, str])
async def generate_component_form(
    request: str = Form(..., description="JSON string of ComponentRequest"),
    image: Optional[UploadFile] = File(None),
    options: Optional[str] = Form(None, description="JSON string of GenerationOptions"),
    orchestrator: AgentOrchestrator = Depends(get_orchestrator)
):
    """Generate AEM component from form data (for multipart/form-data requests)"""
    
    try:
        # Parse JSON strings
        try:
            request_data = json.loads(request)
            component_request = ComponentRequest(**request_data)
        except (json.JSONDecodeError, ValueError) as e:
            raise HTTPException(status_code=422, detail=f"Invalid request JSON: {str(e)}")
        
        # Parse options if provided
        generation_options = GenerationOptions()
        if options:
            try:
                options_data = json.loads(options)
                generation_options = GenerationOptions(**options_data)
            except (json.JSONDecodeError, ValueError) as e:
                raise HTTPException(status_code=422, detail=f"Invalid options JSON: {str(e)}")
        
        # Handle image upload if provided
        image_url = None
        if image:
            file_handler = FileHandler()
            image_url = await file_handler.upload_image(image)
        
        # Prepare request data
        final_request_data = {
            "description": component_request.description,
            "component_type": component_request.component_type,
            "fields": [field.dict() for field in component_request.fields] if component_request.fields else None,
            "image_url": image_url,
            "project_namespace": component_request.project_namespace,
            "component_group": component_request.component_group,
            "options": generation_options.dict()
        }
        
        # Start generation process
        request_id = await orchestrator.generate_component(final_request_data)
        
        return {
            "request_id": request_id,
            "message": "Component generation started",
            "status_url": f"/api/v1/components/status/{request_id}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating component: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status/{request_id}", response_model=GenerationStatus)
async def get_generation_status(
    request_id: str,
    orchestrator: AgentOrchestrator = Depends(get_orchestrator)
):
    """Get component generation status"""
    
    try:
        status = await orchestrator.get_status(request_id)
        
        return GenerationStatus(
            request_id=request_id,
            status=status.get("status"),
            progress=status.get("progress", 0),
            current_step=status.get("current_step", ""),
            estimated_completion=status.get("estimated_completion")
        )
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/result/{request_id}", response_model=ComponentResponse)
async def get_generation_result(
    request_id: str,
    orchestrator: AgentOrchestrator = Depends(get_orchestrator)
):
    """Get generated component files"""
    
    try:
        # Get result from queue
        result = await orchestrator.task_queue.get_result(request_id)
        
        if not result:
            raise HTTPException(status_code=404, detail="Result not found")
        
        if result.get("status") != "completed":
            raise HTTPException(status_code=400, detail=f"Generation status: {result.get('status')}")
        
        return ComponentResponse(**result)
        
    except Exception as e:
        logger.error(f"Error getting result: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-sync", response_model=ComponentResponse)
async def generate_component_sync(
    request: ComponentRequest,
    image: Optional[UploadFile] = File(None),
    options: Optional[GenerationOptions] = None,
    orchestrator: AgentOrchestrator = Depends(get_orchestrator)
):
    """Generate AEM component synchronously (for smaller components)"""
    
    try:
        # This endpoint waits for completion
        image_url = None
        if image:
            file_handler = FileHandler()
            image_url = await file_handler.upload_image(image)
        
        request_data = {
            "description": request.description,
            "component_type": request.component_type,
            "fields": [field.dict() for field in request.fields] if request.fields else None,
            "image_url": image_url,
            "project_namespace": request.project_namespace,
            "component_group": request.component_group,
            "options": options.dict() if options else GenerationOptions().dict()
        }
        
        # Generate and wait for result
        request_id = await orchestrator.generate_component(request_data)
        
        # Poll for completion (with timeout)
        max_attempts = 60  # 5 minutes with 5 second intervals
        for _ in range(max_attempts):
            await asyncio.sleep(5)
            result = await orchestrator.task_queue.get_result(request_id)
            
            if result and result.get("status") == "completed":
                return ComponentResponse(**result)
            elif result and result.get("status") == "failed":
                raise HTTPException(status_code=500, detail="Generation failed")
        
        raise HTTPException(status_code=408, detail="Request timeout")
        
    except Exception as e:
        logger.error(f"Error in sync generation: {e}")
        raise HTTPException(status_code=500, detail=str(e))