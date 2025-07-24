from typing import Dict, Any, Optional
from app.agents.base import BaseAgent
from app.config import settings
import json
import re

class ComponentGenerator(BaseAgent):
    """Agent for generating complete AEM components"""
    
    def __init__(self):
        super().__init__("component_generator")
        self.use_claude = False  # Temporarily disable Claude, use OpenAI only
    
    def get_system_prompt(self) -> str:
        return """You are an expert AEM Component Generator. Create a complete, production-ready AEM component using the requirements and extracted code.

CRITICAL REQUIREMENTS:
1. **HTL Templates MUST use data-sly-use directive** to include Sling Models
2. **Package names must be configurable** and follow provided package structure
3. **All code must be complete and functional** - no placeholders, TODOs, or truncation
4. **Follow AEM best practices** and naming conventions
5. **Include proper error handling and validation**
6. **Ensure accessibility compliance** (WCAG 2.1 AA)
7. **Implement responsive design**
8. **Add comprehensive JavaDoc and code comments**

HTL TEMPLATE REQUIREMENTS:
- MUST start with: <div data-sly-use.model="[SLING_MODEL_CLASS]">
- Use ${model.propertyName} to access Sling Model properties
- Include proper conditional rendering with data-sly-test
- Add ARIA attributes for accessibility
- Use semantic HTML elements
- Include CSS classes that match the component name

SLING MODEL REQUIREMENTS:
- Use the provided package name (configurable)
- Include proper @Model annotation with adaptables=Resource.class
- Use @ValueMapValue for property injection with proper InjectionStrategy
- Include null safety checks and default values
- Add comprehensive JavaDoc
- Follow AEM best practices for resource adaptation

DIALOG REQUIREMENTS:
- Complete XML with proper namespaces
- All form fields must match Sling Model properties
- Include validation rules and help text
- Use appropriate Granite UI components
- Group related fields logically

CLIENT LIBRARY REQUIREMENTS:
- Complete CSS with responsive design
- JavaScript with proper initialization
- Categories and dependencies properly configured
- Performance optimized code

PROJECT STRUCTURE OUTPUT:
Generate files that follow standard AEM project structure:
- HTL: ui.apps/src/main/content/jcr_root/apps/[appId]/components/[componentName]/[componentName].html
- Sling Model: core/src/main/java/[packagePath]/models/[ComponentName]Model.java
- Dialog: ui.apps/src/main/content/jcr_root/apps/[appId]/components/[componentName]/_cq_dialog/.content.xml
- Content XML: ui.apps/src/main/content/jcr_root/apps/[appId]/components/[componentName]/.content.xml

OUTPUT STRUCTURE (Single JSON response):
{
  "htl": "complete HTL template with data-sly-use directive",
  "slingModel": "complete Java Sling Model class with proper package",
  "dialog": "complete dialog XML configuration",
  "contentXml": "complete .content.xml file",
  "clientlibs": {
    "css": "complete responsive CSS file",
    "js": "complete JavaScript file with initialization",
    "categoriesXml": "complete .content.xml for clientlib categories"
  },
  "projectStructure": {
    "htlPath": "ui.apps/src/main/content/jcr_root/apps/[appId]/components/[componentName]/[componentName].html",
    "slingModelPath": "core/src/main/java/[packagePath]/models/[ComponentName]Model.java",
    "dialogPath": "ui.apps/src/main/content/jcr_root/apps/[appId]/components/[componentName]/_cq_dialog/.content.xml",
    "contentXmlPath": "ui.apps/src/main/content/jcr_root/apps/[appId]/components/[componentName]/.content.xml",
    "clientlibPath": "ui.apps/src/main/content/jcr_root/apps/[appId]/components/[componentName]/clientlibs"
  }
}

EXAMPLE HTL STRUCTURE:
<div data-sly-use.model="com.mycompany.myproject.core.models.MyComponentModel" class="my-component">
    <h2 data-sly-test="${model.title}">${model.title}</h2>
    <p data-sly-test="${model.description}">${model.description}</p>
</div>"""
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate complete AEM component"""
        
        requirements = input_data.get('requirements', {})
        extracted_code = input_data.get('extracted_code', {})
        options = input_data.get('options', {})
        
        # Build comprehensive prompt
        prompt = self._build_generation_prompt(requirements, extracted_code, options)
        
        # Use Claude for better code generation
        if self.use_claude and self.anthropic_client:
            response = await self.call_claude(prompt)
        else:
            response = await self.call_gpt4(prompt, max_tokens=4000)  # Reduced token limit for OpenAI
        
        result = self.parse_json_response(response)
        
        # Post-process the generated code with options
        result = self._post_process_generation(result, requirements, options)
        
        return result
    
    def _build_generation_prompt(self, requirements: Dict, extracted_code: Dict, options: Dict) -> str:
        """Build detailed generation prompt"""
        
        # Extract configuration
        component_metadata = requirements.get('componentMetadata', {})
        component_name = component_metadata.get('name', 'component')
        display_name = component_metadata.get('displayName', 'Component')
        group = component_metadata.get('group', 'Custom')
        
        # Get package configuration from options or use defaults from settings
        app_id = options.get('app_id', options.get('appId', settings.DEFAULT_APP_ID))  # Support both naming conventions
        package_name = options.get('package_name', options.get('packageName', settings.DEFAULT_PACKAGE_NAME))  # Support both naming conventions
        package_path = package_name.replace('.', '/')
        
        # Build the complete component class name
        component_class_name = f"{component_name.title().replace('-', '')}Model"
        full_model_class = f"{package_name}.core.models.{component_class_name}"
        
        prompt = f"""Generate a complete AEM component based on these specifications:

CONFIGURATION:
- App ID: {app_id}
- Package Name: {package_name}
- Package Path: {package_path}
- Component Name: {component_name}
- Display Name: {display_name}
- Component Group: {group}
- Sling Model Class: {full_model_class}

REQUIREMENTS:
{json.dumps(requirements, indent=2)}

EXTRACTED UI CODE (if provided):
{json.dumps(extracted_code, indent=2)}

GENERATION OPTIONS:
{json.dumps(options, indent=2)}

CRITICAL IMPLEMENTATION REQUIREMENTS:

1. **HTL Template Requirements:**
   - MUST start with: <div data-sly-use.model="{full_model_class}" class="{component_name}">
   - Use ${{model.propertyName}} to access all Sling Model properties
   - Include data-sly-test for conditional rendering
   - Add proper ARIA attributes and semantic HTML
   - Include CSS classes that match component name: {component_name}

2. **Sling Model Requirements:**
   - Package: {package_name}.core.models
   - Class name: {component_class_name}
   - @Model(adaptables = Resource.class, resourceType = "{app_id}/components/{component_name}")
   - Use @ValueMapValue with proper InjectionStrategy.OPTIONAL
   - Include @PostConstruct method if needed
   - Add null safety checks and default values

3. **Dialog Requirements:**
   - Must include all properties that exist in the Sling Model
   - Use appropriate Granite UI components
   - Include proper validation and help text
   - Resource type: {app_id}/components/{component_name}

4. **Content XML Requirements:**
   - jcr:primaryType="cq:Component"
   - sling:resourceType="{app_id}/components/{component_name}"
   - componentGroup="{group}"
   - jcr:title="{display_name}"

5. **Project Structure:**
   - HTL: ui.apps/src/main/content/jcr_root/apps/{app_id}/components/{component_name}/{component_name}.html
   - Sling Model: core/src/main/java/{package_path}/core/models/{component_class_name}.java
   - Dialog: ui.apps/src/main/content/jcr_root/apps/{app_id}/components/{component_name}/_cq_dialog/.content.xml
   - Content: ui.apps/src/main/content/jcr_root/apps/{app_id}/components/{component_name}/.content.xml

Generate ALL files with complete, production-ready code. No placeholders, TODOs, or truncation.
Ensure the HTL template properly uses the data-sly-use directive to include the Sling Model."""

        return prompt
    
    def _post_process_generation(self, generated: Dict, requirements: Dict, options: Optional[Dict] = None) -> Dict:
        """Post-process generated code to ensure quality and consistency"""
        
        if options is None:
            options = {}
            
        # Extract configuration
        metadata = requirements.get('componentMetadata', {})
        component_name = metadata.get('name', 'component')
        app_id = options.get('app_id', options.get('appId', settings.DEFAULT_APP_ID)) if options else settings.DEFAULT_APP_ID
        package_name = options.get('package_name', options.get('packageName', settings.DEFAULT_PACKAGE_NAME)) if options else settings.DEFAULT_PACKAGE_NAME
        
        # Ensure all required files are present
        required_files = ['slingModel', 'htl', 'dialog', 'contentXml']
        for file in required_files:
            if not generated.get(file):
                self.logger.warning(f"Missing required file: {file}")
                generated[file] = self._generate_fallback_content(file, component_name, package_name, app_id)
        
        # Fix HTL to ensure it uses data-sly-use
        if 'htl' in generated:
            generated['htl'] = self._fix_htl_template(generated['htl'], component_name, package_name, app_id)
        
        # Fix Sling Model package declaration
        if 'slingModel' in generated:
            generated['slingModel'] = self._fix_sling_model_package(
                generated['slingModel'], 
                component_name, 
                package_name,
                app_id
            )
        
        # Add project structure paths
        generated['projectStructure'] = self._generate_project_structure(
            component_name, package_name, app_id
        )
        
        return generated
    
    def _fix_htl_template(self, htl_content: str, component_name: str, package_name: str, app_id: str) -> str:
        """Ensure HTL template uses data-sly-use directive properly"""
        
        component_class_name = f"{component_name.title().replace('-', '')}Model"
        full_model_class = f"{package_name}.core.models.{component_class_name}"
        
        # Check if data-sly-use is already present
        if 'data-sly-use' not in htl_content:
            # Try to add data-sly-use directive to the first HTML element
            
            # Look for the first opening HTML tag
            first_tag_match = re.search(r'<(\w+)([^>]*?)>', htl_content)
            if first_tag_match:
                tag_name = first_tag_match.group(1)
                existing_attrs = first_tag_match.group(2)
                
                # Create the new opening tag with data-sly-use
                new_opening_tag = f'<{tag_name} data-sly-use.model="{full_model_class}"{existing_attrs}>'
                
                # Replace the first occurrence
                htl_content = htl_content.replace(first_tag_match.group(0), new_opening_tag, 1)
            else:
                # If no HTML tags found, wrap the entire content
                htl_content = f'<div data-sly-use.model="{full_model_class}" class="{component_name}">\n{htl_content}\n</div>'
        else:
            # If data-sly-use exists but might have the wrong class, update it
            htl_content = re.sub(
                r'data-sly-use\.\w+="[^"]*"',
                f'data-sly-use.model="{full_model_class}"',
                htl_content
            )
        
        return htl_content
    
    def _fix_sling_model_package(self, sling_model: str, component_name: str, package_name: str, app_id: str) -> str:
        """Fix Sling Model package and ensure proper annotations"""
        
        component_class_name = f"{component_name.title().replace('-', '')}Model"
        proper_package = f"{package_name}.core.models"
        resource_type = f"{app_id}/components/{component_name}"
        
        # Replace generic package with proper one
        
        # Fix package declaration - be more aggressive in replacing any existing package
        if 'package ' in sling_model:
            sling_model = re.sub(r'package [^;]+;', f'package {proper_package};', sling_model)
        else:
            sling_model = f'package {proper_package};\n\n{sling_model}'
        
        # Ensure proper @Model annotation with resourceType
        if '@Model' in sling_model:
            if 'resourceType' not in sling_model:
                sling_model = re.sub(
                    r'@Model\([^)]*\)',
                    f'@Model(adaptables = Resource.class, resourceType = "{resource_type}")',
                    sling_model
                )
            else:
                # Update existing resourceType
                sling_model = re.sub(
                    r'resourceType\s*=\s*"[^"]*"',
                    f'resourceType = "{resource_type}"',
                    sling_model
                )
        
        # Ensure proper class name
        if f'class {component_class_name}' not in sling_model and f'interface {component_class_name}' not in sling_model:
            # Replace any existing class/interface name
            sling_model = re.sub(
                r'(public\s+(?:class|interface)\s+)\w+',
                rf'\1{component_class_name}',
                sling_model
            )
        
        return sling_model
    
    def _generate_project_structure(self, component_name: str, package_name: str, app_id: str) -> Dict:
        """Generate project structure paths"""
        
        package_path = package_name.replace('.', '/')
        component_class_name = f"{component_name.title().replace('-', '')}Model"
        
        return {
            "htlPath": f"ui.apps/src/main/content/jcr_root/apps/{app_id}/components/{component_name}/{component_name}.html",
            "slingModelPath": f"core/src/main/java/{package_path}/core/models/{component_class_name}.java",
            "dialogPath": f"ui.apps/src/main/content/jcr_root/apps/{app_id}/components/{component_name}/_cq_dialog/.content.xml",
            "contentXmlPath": f"ui.apps/src/main/content/jcr_root/apps/{app_id}/components/{component_name}/.content.xml",
            "clientlibCssPath": f"ui.apps/src/main/content/jcr_root/apps/{app_id}/components/{component_name}/clientlibs/css/{component_name}.css",
            "clientlibJsPath": f"ui.apps/src/main/content/jcr_root/apps/{app_id}/components/{component_name}/clientlibs/js/{component_name}.js",
            "clientlibConfigPath": f"ui.apps/src/main/content/jcr_root/apps/{app_id}/components/{component_name}/clientlibs/.content.xml"
        }
    
    def _generate_fallback_content(self, file_type: str, component_name: str, package_name: str, app_id: str) -> str:
        """Generate fallback content for missing files"""
        
        if file_type == 'htl':
            return f'''<div data-sly-use.model="{package_name}.core.models.{component_name.title().replace('-', '')}Model" class="{component_name}">
    <h2 data-sly-test="${{model.title}}">${{model.title}}</h2>
    <p data-sly-test="${{model.description}}">${{model.description}}</p>
</div>'''
        
        elif file_type == 'slingModel':
            return f'''package {package_name}.core.models;

import org.apache.sling.api.resource.Resource;
import org.apache.sling.models.annotations.Default;
import org.apache.sling.models.annotations.Model;
import org.apache.sling.models.annotations.injectorspecific.InjectionStrategy;
import org.apache.sling.models.annotations.injectorspecific.ValueMapValue;

@Model(adaptables = Resource.class, resourceType = "{app_id}/components/{component_name}")
public class {component_name.title().replace('-', '')}Model {{
    
    @ValueMapValue(injectionStrategy = InjectionStrategy.OPTIONAL)
    @Default(values = "")
    private String title;
    
    @ValueMapValue(injectionStrategy = InjectionStrategy.OPTIONAL)
    @Default(values = "")
    private String description;
    
    public String getTitle() {{
        return title;
    }}
    
    public String getDescription() {{
        return description;
    }}
}}'''
        
        return ""

