from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, BackgroundTasks, Form
from fastapi.responses import JSONResponse
from typing import Optional, Dict, Any
import logging
import json
import asyncio

from app.models.requests import ComponentRequest, GenerationOptions
from app.models.responses import ComponentResponse, GenerationStatus
from app.utils.file_handler import FileHandler
from app.agents.orchestrator import AgentOrchestrator
from app.services.project_organizer import ProjectOrganizerService
from app.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)

async def organize_component_background(component_data: Dict[str, Any]):
    """Background task to organize component into project structure"""
    try:
        if settings.AUTO_ORGANIZE_COMPONENTS:
            organizer = ProjectOrganizerService()
            result = await organizer.organize_component(component_data)
            logger.info(f"Background organization result: {result}")
    except Exception as e:
        logger.error(f"Background organization failed: {str(e)}")
        # Don't raise exception to avoid breaking the main flow

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
            try:
                file_handler = FileHandler()
                image_url = await file_handler.upload_image(image)
            except ValueError as e:
                raise HTTPException(status_code=400, detail=f"Image validation error: {str(e)}")
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Image upload failed: {str(e)}")
        
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
        logger.info(f"Received generate-form request:")
        logger.info(f"  - Request JSON: {request}")
        logger.info(f"  - Image: {image.filename if image else 'None'} (size: {image.size if image else 'N/A'})")
        logger.info(f"  - Options JSON: {options}")
        
        # Parse JSON strings
        try:
            request_data = json.loads(request)
            component_request = ComponentRequest(**request_data)
            logger.info(f"  - Parsed ComponentRequest: {component_request}")
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Invalid request JSON: {str(e)}")
            raise HTTPException(status_code=422, detail=f"Invalid request JSON: {str(e)}")
        
        # Parse options if provided
        generation_options = GenerationOptions()
        if options:
            try:
                options_data = json.loads(options)
                generation_options = GenerationOptions(**options_data)
                logger.info(f"  - Parsed GenerationOptions: {generation_options}")
            except (json.JSONDecodeError, ValueError) as e:
                logger.error(f"Invalid options JSON: {str(e)}")
                raise HTTPException(status_code=422, detail=f"Invalid options JSON: {str(e)}")
        
        # Handle image upload if provided
        image_url = None
        if image:
            logger.info(f"Processing image upload: {image.filename}, content_type: {image.content_type}")
            try:
                file_handler = FileHandler()
                image_url = await file_handler.upload_image(image)
                logger.info(f"Image upload successful. Data URL length: {len(image_url) if image_url else 0}")
            except ValueError as e:
                logger.error(f"Image validation error: {str(e)}")
                raise HTTPException(status_code=400, detail=f"Image validation error: {str(e)}")
            except Exception as e:
                logger.error(f"Image upload failed: {str(e)}")
                raise HTTPException(status_code=500, detail=f"Image upload failed: {str(e)}")
        else:
            logger.info("No image provided in request")
        
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
        
        logger.info(f"Final request data prepared:")
        logger.info(f"  - Description: {final_request_data['description']}")
        logger.info(f"  - Component type: {final_request_data['component_type']}")
        logger.info(f"  - Fields count: {len(final_request_data['fields']) if final_request_data['fields'] else 0}")
        logger.info(f"  - Image URL present: {bool(final_request_data['image_url'])}")
        logger.info(f"  - Project namespace: {final_request_data['project_namespace']}")
        logger.info(f"  - Component group: {final_request_data['component_group']}")
        
        # Start generation process
        request_id = await orchestrator.generate_component(final_request_data)
        logger.info(f"Generation started with request_id: {request_id}")
        
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
    background_tasks: BackgroundTasks,
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
        
        # Add background task to organize component into project structure
        if settings.AUTO_ORGANIZE_COMPONENTS:
            background_tasks.add_task(organize_component_background, result)
            logger.info(f"Added background task to organize component: {result.get('component_name', 'unknown')}")
        
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
            try:
                file_handler = FileHandler()
                image_url = await file_handler.upload_image(image)
            except ValueError as e:
                raise HTTPException(status_code=400, detail=f"Image validation error: {str(e)}")
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Image upload failed: {str(e)}")
        
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

@router.get("/preview/{request_id}")
async def get_component_preview(
    request_id: str,
    orchestrator: AgentOrchestrator = Depends(get_orchestrator)
):
    """Get component preview data (HTML and CSS from image analysis)"""
    
    try:
        # Get result from queue
        result = await orchestrator.task_queue.get_result(request_id)
        
        if not result:
            raise HTTPException(status_code=404, detail="Component not found")
        
        # Extract preview data from metadata (for image-generated components)
        metadata = result.get("metadata", {})
        extracted_code = metadata.get("extracted_code", {})
        
        # Check if component was generated from image (has extracted_code)
        if extracted_code:
            # Use extracted code from image analysis
            html_data = extracted_code.get("html", {})
            css_data = extracted_code.get("css", {})
            js_data = extracted_code.get("javascript", {})
            
            preview_data = {
                "request_id": request_id,
                "component_name": result.get("component_name", "Unknown Component"),
                "html": {
                    "structure": html_data.get("structure", ""),
                    "elements": html_data.get("semanticElements", []),
                    "classes": html_data.get("cssClasses", [])
                },
                "css": {
                    "styles": css_data.get("styles", ""),
                    "variables": css_data.get("variables", {}),
                    "responsive": css_data.get("responsive", {})
                },
                "javascript": {
                    "required": js_data.get("required", False),
                    "code": js_data.get("code", ""),
                    "functionality": js_data.get("functionality", [])
                },
                "metadata": {
                    "generated_from_image": True,
                    "created_at": result.get("created_at")
                }
            }
        else:
            # Use generated HTL and CSS files for text-based components
            files = result.get("files", {})
            clientlibs = files.get("clientlibs", {})
            
            if not files.get("htl") and not clientlibs.get("css"):
                raise HTTPException(status_code=404, detail="No preview data available - component has no HTML or CSS content")
            
            preview_data = {
                "request_id": request_id,
                "component_name": result.get("component_name", "Unknown Component"),
                "html": {
                    "structure": files.get("htl", ""),
                    "elements": [],
                    "classes": []
                },
                "css": {
                    "styles": clientlibs.get("css", ""),
                    "variables": {},
                    "responsive": {}
                },
                "javascript": {
                    "required": bool(clientlibs.get("js")),
                    "code": clientlibs.get("js", ""),
                    "functionality": []
                },
                "metadata": {
                    "generated_from_image": False,
                    "created_at": result.get("created_at")
                }
            }
        
        return preview_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting preview: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/test-organize")
async def test_organize_component():
    """Test endpoint to verify project organizer functionality"""
    try:
        from ..services.project_organizer import ProjectOrganizerService
        
        # Test data
        test_component_data = {
            "component_name": "test-button",
            "files": {
                "htl": "<div class='test-button'><p>Test Component</p></div>",
                "sling_model": "package com.example;\n\n@Model(adaptables = Resource.class)\npublic class TestButton {\n    // Test model\n}",
                "dialog": "<?xml version='1.0'?><jcr:root><items><label/></items></jcr:root>",
                "clientlibs": {
                    "css": ".test-button { background: blue; }",
                    "js": "console.log('test button loaded');"
                }
            },
            "metadata": {
                "requirements": {
                    "componentMetadata": {
                        "displayName": "Test Button Component"
                    }
                }
            }
        }
        
        organizer = ProjectOrganizerService()
        result = await organizer.organize_component(test_component_data)
        
        return {"message": "Test completed", "result": result}
        
    except Exception as e:
        logger.error(f"Test organization failed: {str(e)}")
        return {"error": str(e), "message": "Test failed"}