from pydantic import BaseModel
from typing import Dict, List, Optional, Any
from datetime import datetime

class ComponentFiles(BaseModel):
    sling_model: str
    sling_model_impl: Optional[str]
    htl: str
    dialog: str
    content_xml: str
    clientlibs: Dict[str, str]
    junit: Optional[str]

class ValidationResult(BaseModel):
    status: str
    score: int
    issues: List[str]
    suggestions: List[str]

class ComponentResponse(BaseModel):
    request_id: str
    status: str
    component_name: str
    component_type: str
    files: ComponentFiles
    validation: Optional[ValidationResult]
    metadata: Dict[str, Any]
    created_at: datetime

class GenerationStatus(BaseModel):
    request_id: str
    status: str
    progress: int
    current_step: str
    estimated_completion: Optional[datetime]

