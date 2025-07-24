from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum
from app.config import settings

class ComponentType(str, Enum):
    HERO_BANNER = "hero-banner"
    CAROUSEL = "carousel"
    ACCORDION = "accordion"
    TABS = "tabs"
    CARD = "card"
    CUSTOM = "custom"

class FieldType(str, Enum):
    TEXTFIELD = "textfield"
    TEXTAREA = "textarea"
    RICHTEXT = "richtext"
    PATHFIELD = "pathfield"
    SELECT = "select"
    CHECKBOX = "checkbox"
    MULTIFIELD = "multifield"

class ComponentField(BaseModel):
    name: str
    label: str
    type: FieldType
    required: bool = False
    description: Optional[str] = None
    default_value: Optional[Any] = None
    validation: Optional[Dict[str, Any]] = None

class ComponentRequest(BaseModel):
    description: str = Field(..., description="Natural language description of the component")
    component_type: Optional[ComponentType] = None
    fields: Optional[List[ComponentField]] = None
    image_url: Optional[str] = None
    project_namespace: str = Field(default="wknd", description="AEM project namespace")
    component_group: str = Field(default="WKND.Content", description="Component group")
    
class GenerationOptions(BaseModel):
    include_tests: bool = True
    include_clientlibs: bool = True
    include_impl: bool = True
    responsive: bool = True
    accessibility: bool = True
    use_core_components: bool = True
    app_id: str = Field(default_factory=lambda: settings.DEFAULT_APP_ID, description="Application ID for resource types and package structure")
    package_name: str = Field(default_factory=lambda: settings.DEFAULT_PACKAGE_NAME, description="Base package name for Java classes")
