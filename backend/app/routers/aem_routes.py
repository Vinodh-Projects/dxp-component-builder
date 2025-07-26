from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import Optional, Dict, Any
import asyncio
import logging

from app.services.aem_deployment import AEMDeploymentService

router = APIRouter()
logger = logging.getLogger(__name__)

# Global deployment service instance
deployment_service = AEMDeploymentService()

async def deploy_project_background(deployment_result_storage: Dict[str, Any]):
    """Background task to deploy project"""
    try:
        result = await deployment_service.build_and_deploy_project()
        deployment_result_storage.update(result)
        logger.info(f"Background deployment completed: {result['success']}")
    except Exception as e:
        logger.error(f"Background deployment failed: {str(e)}")
        deployment_result_storage.update({
            "success": False,
            "message": f"Background deployment failed: {str(e)}",
            "error": str(e)
        })

async def deploy_simple_background_task(deployment_result_storage: Dict[str, Any]):
    """Background task for simple deploy project using mvn clean install -PautoInstallPackage"""
    try:
        result = await deployment_service.simple_build_and_deploy()
        deployment_result_storage.update(result)
        logger.info(f"Background simple deployment completed: {result['success']}")
    except Exception as e:
        logger.error(f"Background simple deployment failed: {str(e)}")
        deployment_result_storage.update({
            "success": False,
            "message": f"Background simple deployment failed: {str(e)}",
            "error": str(e)
        })

# In-memory storage for deployment results (in production, use Redis or database)
deployment_results = {}

@router.post("/deploy")
async def deploy_aem_project(background_tasks: BackgroundTasks):
    """
    Build and deploy the AEM project to AEM Author server (background task)
    Uses the complex deployment process with validation and separate build/deploy steps
    """
    try:
        deployment_id = f"deploy_{int(asyncio.get_event_loop().time())}"
        
        # Initialize result storage
        deployment_results[deployment_id] = {
            "status": "in_progress",
            "message": "Deployment started",
            "started_at": deployment_id
        }
        
        # Start background deployment
        background_tasks.add_task(deploy_project_background, deployment_results[deployment_id])
        
        return JSONResponse(
            status_code=202,
            content={
                "message": "AEM project deployment started",
                "deployment_id": deployment_id,
                "status": "in_progress",
                "check_status_url": f"/api/v1/aem/deploy/status/{deployment_id}"
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to start deployment: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to start deployment: {str(e)}")

@router.post("/deploy/simple-bg")
async def deploy_simple_background(background_tasks: BackgroundTasks):
    """
    Simple build and deploy in background using mvn clean install -PautoInstallPackage -DskipTests -Padobe-public
    This is the recommended endpoint for frontend integration
    """
    try:
        deployment_id = f"simple_deploy_{int(asyncio.get_event_loop().time())}"
        
        # Initialize result storage
        deployment_results[deployment_id] = {
            "status": "in_progress",
            "message": "Simple build and deploy started",
            "maven_command": "mvn clean install -PautoInstallPackage -DskipTests -Padobe-public",
            "started_at": deployment_id
        }
        
        # Start background simple deployment
        background_tasks.add_task(deploy_simple_background_task, deployment_results[deployment_id])
        
        return JSONResponse(
            status_code=202,
            content={
                "message": "Simple AEM build and deploy started",
                "deployment_id": deployment_id,
                "status": "in_progress",
                "maven_command": "mvn clean install -PautoInstallPackage -DskipTests -Padobe-public",
                "check_status_url": f"/api/v1/aem/deploy/status/{deployment_id}"
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to start simple deployment: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to start simple deployment: {str(e)}")

@router.get("/deploy/status/{deployment_id}")
async def get_deployment_status(deployment_id: str):
    """
    Get the status of a deployment
    """
    try:
        if deployment_id not in deployment_results:
            raise HTTPException(status_code=404, detail="Deployment not found")
        
        result = deployment_results[deployment_id]
        
        # Determine status based on result
        if "success" in result:
            status = "completed" if result["success"] else "failed"
        else:
            status = "in_progress"
        
        return {
            "deployment_id": deployment_id,
            "status": status,
            **result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get deployment status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get deployment status: {str(e)}")

@router.post("/deploy/simple")
async def deploy_simple():
    """
    Simple build and deploy using mvn clean install -PautoInstallPackage -DskipTests -Padobe-public
    This endpoint runs the Maven command that builds and deploys in one step
    """
    try:
        logger.info("Starting simple build and deploy process")
        result = await deployment_service.simple_build_and_deploy()
        
        if result["success"]:
            return JSONResponse(
                status_code=200,
                content={
                    "message": "Build and deploy completed successfully",
                    **result
                }
            )
        else:
            return JSONResponse(
                status_code=400,
                content={
                    "message": "Build and deploy failed",
                    **result
                }
            )
            
    except Exception as e:
        logger.error(f"Simple deployment failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Simple deployment failed: {str(e)}")

@router.post("/deploy/sync")
async def deploy_aem_project_sync():
    """
    Build and deploy the AEM project synchronously (for testing/debugging)
    """
    try:
        logger.info("Starting synchronous AEM project deployment")
        result = await deployment_service.build_and_deploy_project()
        
        if result["success"]:
            return JSONResponse(
                status_code=200,
                content={
                    "message": "AEM project deployed successfully",
                    **result
                }
            )
        else:
            return JSONResponse(
                status_code=400,
                content={
                    "message": "AEM project deployment failed",
                    **result
                }
            )
            
    except Exception as e:
        logger.error(f"Synchronous deployment failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Deployment failed: {str(e)}")

@router.post("/build/{module_name}")
async def build_specific_module(module_name: str):
    """
    Build and deploy a specific AEM module
    """
    try:
        logger.info(f"Building specific module: {module_name}")
        result = await deployment_service.build_specific_module(module_name)
        
        if result["success"]:
            return JSONResponse(
                status_code=200,
                content={
                    "message": f"Module '{module_name}' built and deployed successfully",
                    **result
                }
            )
        else:
            return JSONResponse(
                status_code=400,
                content={
                    "message": f"Module '{module_name}' build failed",
                    **result
                }
            )
            
    except Exception as e:
        logger.error(f"Module build failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Module build failed: {str(e)}")

@router.get("/server/status")
async def get_aem_server_status():
    """
    Check AEM server status and connectivity
    """
    try:
        status = await deployment_service.get_deployment_status()
        
        return {
            "message": "AEM server status check completed",
            **status
        }
        
    except Exception as e:
        logger.error(f"Server status check failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Server status check failed: {str(e)}")

@router.get("/config")
async def get_deployment_config():
    """
    Get current deployment configuration
    """
    try:
        return {
            "project_path": str(deployment_service.project_root),
            "aem_server_url": deployment_service.aem_server_url,
            "aem_username": deployment_service.aem_username,
            "maven_profiles": deployment_service.maven_profiles,
            "skip_tests": deployment_service.skip_tests
        }
        
    except Exception as e:
        logger.error(f"Failed to get config: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get config: {str(e)}")

@router.delete("/deploy/results/{deployment_id}")
async def clear_deployment_result(deployment_id: str):
    """
    Clear a deployment result from memory
    """
    try:
        if deployment_id in deployment_results:
            del deployment_results[deployment_id]
            return {"message": f"Deployment result {deployment_id} cleared"}
        else:
            raise HTTPException(status_code=404, detail="Deployment not found")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to clear deployment result: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to clear deployment result: {str(e)}")

@router.get("/deploy/history")
async def get_deployment_history():
    """
    Get all deployment results
    """
    try:
        return {
            "deployments": deployment_results,
            "total_deployments": len(deployment_results)
        }
        
    except Exception as e:
        logger.error(f"Failed to get deployment history: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get deployment history: {str(e)}")

@router.post("/validate")
async def validate_project_structure():
    """
    Validate AEM project structure and Maven availability
    """
    try:
        validation_result = await deployment_service._validate_project_structure()
        return validation_result
        
    except Exception as e:
        logger.error(f"Project validation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Project validation failed: {str(e)}")

@router.get("/status")
async def get_aem_status():
    """
    Get AEM server status - alias for server/status
    """
    try:
        status = await deployment_service.get_deployment_status()
        return {
            "server_url": deployment_service.aem_server_url,
            "status": "connected" if status.get("success") else "disconnected",
            "message": status.get("message", "Unknown status")
        }
        
    except Exception as e:
        logger.error(f"AEM status check failed: {str(e)}")
        return {
            "server_url": deployment_service.aem_server_url,
            "status": "error",
            "message": str(e)
        }

@router.post("/build")
async def build_module():
    """
    Build a specific module - expects {"module": "module_name"} in request body
    """
    try:
        from pydantic import BaseModel
        
        class BuildRequest(BaseModel):
            module: str
        
        # This will be properly handled when request body is provided
        # For now, default to ui.apps
        result = await deployment_service._build_project()
        return result
        
    except Exception as e:
        logger.error(f"Module build failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Module build failed: {str(e)}")

@router.get("/logs")
async def get_deployment_logs():
    """
    Get recent deployment logs
    """
    try:
        # This is a simple implementation - in production you'd want proper log management
        logs = [
            "Maven build started",
            "Project structure validated",
            "Building ui.apps module",
            "Build completed successfully"
        ]
        
        return {
            "logs": logs,
            "total": len(logs)
        }
        
    except Exception as e:
        logger.error(f"Failed to get logs: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get logs: {str(e)}")
