"""
Project Organizer Service - Handles organizing generated components into AEM project structure
"""

import os
import shutil
from pathlib import Path
from typing import Dict, Any, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class ProjectOrganizerService:
    """Service to organize generated AEM components into proper project structure"""
    
    def __init__(self):
        # Use relative import to avoid circular import issues
        try:
            from ..config import settings
            self.project_root = Path(settings.PROJECT_CODE_PATH)
            self.app_id = settings.DEFAULT_APP_ID
            self.package_name = settings.DEFAULT_PACKAGE_NAME
            self.ai_subfolder = settings.AI_COMPONENTS_SUBFOLDER
            self.backup_enabled = settings.BACKUP_EXISTING_COMPONENTS
        except ImportError:
            # Fallback values
            self.project_root = Path("./project_code")
            self.app_id = "myapp"
            self.package_name = "com.mycompany.myapp"
            self.ai_subfolder = "myappai"
            self.backup_enabled = True
        
    async def organize_component(self, component_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Organize a generated component into the AEM project structure
        
        Args:
            component_data: The component data from generation result
            
        Returns:
            Result dictionary with success status and created files
        """
        try:
            component_name = self._extract_component_name(component_data)
            if not component_name:
                raise ValueError("Could not determine component name from generated data")
            
            logger.info(f"Organizing component: {component_name} with app_id: {self.app_id} in AI subfolder: {self.ai_subfolder}")
            
            # Create backup if component exists
            backup_path = None
            if self.backup_enabled:
                backup_path = await self._backup_existing_component(component_name)
            
            # Organize files into project structure
            created_files = await self._organize_files(component_data, component_name)
            
            result = {
                "success": True,
                "message": f"Successfully organized component '{component_name}' into project structure under {self.ai_subfolder}/",
                "component_name": component_name,
                "app_id": self.app_id,
                "ai_subfolder": self.ai_subfolder,
                "created_files": created_files,
                "backup_path": backup_path,
                "organized_at": datetime.now().isoformat()
            }
            
            logger.info(f"Component organization completed: {component_name}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to organize component: {str(e)}")
            # Return success=False but don't raise exception to avoid breaking the main flow
            return {
                "success": False,
                "message": f"Failed to organize component: {str(e)}",
                "component_name": component_data.get('component_name', 'unknown'),
                "error": str(e)
            }
    
    def _extract_component_name(self, component_data: Dict[str, Any]) -> Optional[str]:
        """Extract component name from generated data"""
        # Try multiple possible locations for component name
        possible_names = [
            component_data.get('component_name'),
            component_data.get('name'),
            component_data.get('metadata', {}).get('component_name'),
        ]
        
        for name in possible_names:
            if name and isinstance(name, str):
                # Clean the name to be filesystem-safe
                return name.lower().replace(' ', '-').replace('_', '-')
        
        return None
    
    async def _backup_existing_component(self, component_name: str) -> Optional[str]:
        """Create backup of existing component if it exists"""
        try:
            component_path = self.project_root / "ui.apps" / "src" / "main" / "content" / "jcr_root" / "apps" / self.app_id / "components" / self.ai_subfolder / component_name
            
            if component_path.exists():
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_dir = self.project_root / "backups" / f"{component_name}_{timestamp}"
                backup_dir.mkdir(parents=True, exist_ok=True)
                
                shutil.copytree(component_path, backup_dir / "ui.apps_component")
                
                logger.info(f"Created backup at: {backup_dir}")
                return str(backup_dir)
                
        except Exception as e:
            logger.warning(f"Failed to create backup for {component_name}: {str(e)}")
            
        return None
    
    async def _organize_files(self, component_data: Dict[str, Any], component_name: str) -> Dict[str, str]:
        """Organize component files into AEM project structure"""
        created_files = {}
        
        files = component_data.get('files', {})
        
        # 1. Organize HTL template in ui.apps
        if 'htl' in files:
            htl_path = await self._create_htl_file(component_name, files['htl'])
            if htl_path:
                created_files['htl'] = str(htl_path)
        
        # 2. Organize dialog in ui.apps
        if 'dialog' in files:
            dialog_path = await self._create_dialog_file(component_name, files['dialog'])
            if dialog_path:
                created_files['dialog'] = str(dialog_path)
        
        # 3. Organize Sling Model in core
        if 'sling_model' in files:
            model_path = await self._create_sling_model_file(component_name, files['sling_model'])
            if model_path:
                created_files['sling_model'] = str(model_path)
        
        # 4. Organize client libraries
        if 'clientlibs' in files:
            clientlib_paths = await self._create_clientlib_files(component_name, files['clientlibs'])
            created_files.update(clientlib_paths)
        
        # 5. Create component definition
        component_def_path = await self._create_component_definition(component_name, component_data)
        if component_def_path:
            created_files['component_definition'] = str(component_def_path)
        
        return created_files
    
    async def _create_htl_file(self, component_name: str, htl_content: str) -> Optional[Path]:
        """Create HTL template file in ui.apps"""
        try:
            htl_dir = self.project_root / "ui.apps" / "src" / "main" / "content" / "jcr_root" / "apps" / self.app_id / "components" / self.ai_subfolder / component_name
            htl_dir.mkdir(parents=True, exist_ok=True)
            
            htl_file = htl_dir / f"{component_name}.html"
            htl_file.write_text(htl_content, encoding='utf-8')
            
            logger.info(f"Created HTL file: {htl_file}")
            return htl_file
            
        except Exception as e:
            logger.error(f"Failed to create HTL file: {str(e)}")
            return None
    
    async def _create_dialog_file(self, component_name: str, dialog_content: str) -> Optional[Path]:
        """Create dialog XML file in ui.apps"""
        try:
            dialog_dir = self.project_root / "ui.apps" / "src" / "main" / "content" / "jcr_root" / "apps" / self.app_id / "components" / self.ai_subfolder / component_name / "_cq_dialog"
            dialog_dir.mkdir(parents=True, exist_ok=True)
            
            dialog_file = dialog_dir / ".content.xml"
            dialog_file.write_text(dialog_content, encoding='utf-8')
            
            logger.info(f"Created dialog file: {dialog_file}")
            return dialog_file
            
        except Exception as e:
            logger.error(f"Failed to create dialog file: {str(e)}")
            return None
    
    async def _create_sling_model_file(self, component_name: str, model_content: str) -> Optional[Path]:
        """Create Sling Model Java file in core"""
        try:
            # Convert package name to directory path
            package_path = self.package_name.replace('.', '/')
            model_dir = self.project_root / "core" / "src" / "main" / "java" / package_path / "core" / "models"
            model_dir.mkdir(parents=True, exist_ok=True)
            
            # Create class name (capitalize first letter of each word)
            class_name_base = ''.join(word.capitalize() for word in component_name.split('-'))
            class_name = f"{class_name_base}Model"
            model_file = model_dir / f"{class_name}.java"
            
            # Update package declaration in the content
            updated_content = model_content.replace(
                "package com.example", 
                f"package {self.package_name}.core.models"
            )
            
            model_file.write_text(updated_content, encoding='utf-8')
            
            logger.info(f"Created Sling Model file: {model_file}")
            return model_file
            
        except Exception as e:
            logger.error(f"Failed to create Sling Model file: {str(e)}")
            return None
    
    async def _create_clientlib_files(self, component_name: str, clientlibs: Dict[str, str]) -> Dict[str, str]:
        """Create client library files in ui.apps"""
        created_files = {}
        
        try:
            clientlib_dir = self.project_root / "ui.apps" / "src" / "main" / "content" / "jcr_root" / "apps" / self.app_id / "components" / self.ai_subfolder / component_name / "clientlibs"
            clientlib_dir.mkdir(parents=True, exist_ok=True)
            
            # Create CSS file
            if 'css' in clientlibs:
                css_file = clientlib_dir / f"{component_name}.css"
                css_file.write_text(clientlibs['css'], encoding='utf-8')
                created_files['css'] = str(css_file)
            
            # Create JS file
            if 'js' in clientlibs:
                js_file = clientlib_dir / f"{component_name}.js"
                js_file.write_text(clientlibs['js'], encoding='utf-8')
                created_files['js'] = str(js_file)
            
            # Create .content.xml for clientlib
            clientlib_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<jcr:root xmlns:cq="http://www.day.com/jcr/cq/1.0" xmlns:jcr="http://www.jcp.org/jcr/1.0"
    jcr:primaryType="cq:ClientLibraryFolder"
    categories="[{self.app_id}.{self.ai_subfolder}.components.{component_name}]"
    dependencies="[core.wcm.components.commons.datalayer.v1]"/>
"""
            
            clientlib_xml_file = clientlib_dir / ".content.xml"
            clientlib_xml_file.write_text(clientlib_xml, encoding='utf-8')
            created_files['clientlib_xml'] = str(clientlib_xml_file)
            
            logger.info(f"Created clientlib files in: {clientlib_dir}")
            
        except Exception as e:
            logger.error(f"Failed to create clientlib files: {str(e)}")
        
        return created_files
    
    async def _create_component_definition(self, component_name: str, component_data: Dict[str, Any]) -> Optional[Path]:
        """Create component definition .content.xml file"""
        try:
            component_dir = self.project_root / "ui.apps" / "src" / "main" / "content" / "jcr_root" / "apps" / self.app_id / "components" / self.ai_subfolder / component_name
            component_dir.mkdir(parents=True, exist_ok=True)
            
            # Get component title from metadata or use component name
            title = component_data.get('metadata', {}).get('requirements', {}).get('componentMetadata', {}).get('displayName', component_name.title())
            
            component_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<jcr:root xmlns:cq="http://www.day.com/jcr/cq/1.0" xmlns:jcr="http://www.jcp.org/jcr/1.0"
    jcr:primaryType="cq:Component"
    jcr:title="{title}"
    componentGroup="{self.app_id}.{self.ai_subfolder}.content"/>
"""
            
            component_xml_file = component_dir / ".content.xml"
            component_xml_file.write_text(component_xml, encoding='utf-8')
            
            logger.info(f"Created component definition: {component_xml_file}")
            return component_xml_file
            
        except Exception as e:
            logger.error(f"Failed to create component definition: {str(e)}")
            return None
