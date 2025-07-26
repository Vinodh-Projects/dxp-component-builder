import base64
import os
import json
import re
import shutil
import subprocess
from io import BytesIO
from urllib.request import Request

from google.ai.generativelanguage_v1 import Part
from google.generativeai.types import GenerateContentResponse
from openai import OpenAI, Stream
import google.generativeai as genai
from jinja2 import Environment, FileSystemLoader
from pathlib import Path
from typing import Dict, Any, Coroutine
from dotenv import load_dotenv
import asyncio

import logging
import sys

from openai.types.chat import ChatCompletion, ChatCompletionChunk

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),  # Console output
        logging.FileHandler('app.log')     # File output
    ]
)

# Set logger for your specific module
logger = logging.getLogger('app.services.component_service')
logger.setLevel(logging.INFO)

model = os.getenv("MODEL_PROVIDER", "openai")  # Default to OpenAI if not set

class ComponentService:
    def __init__(self):
        # Load environment variables first
        load_dotenv()

        logger.info(f"In ComponentService")

        if model == "openai":
            logger.info("Using OpenAI model provider")
            api_key = os.getenv("OPENAI_API_KEY")
            self.client = OpenAI(api_key=api_key)

        elif model == "gemini":
            logger.info("Using Gemini model provider")
            api_key = os.getenv("GEMINI_API_KEY")
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-pro')

        if not api_key:
            raise ValueError("API_KEY not found in environment variables")

        template_dir = Path(__file__).parent.parent / "templates"
        self.jinja_env = Environment(loader=FileSystemLoader(template_dir))

    def parse_json_response(self, response: str, agent_name: str) -> Dict[str, Any]:
        """Parse JSON response from LLM"""
        try:
            # Clean the response - remove any non-JSON content
            clean_response = response.replace('```json', '').replace('```', '').strip()

            # Find JSON content between first { and last }
            start_index = clean_response.find('{')
            last_index = clean_response.rfind('}')

            if start_index == -1 or last_index == -1:
                raise ValueError('No valid JSON found in response')

            json_string = clean_response[start_index:last_index + 1]
            return json.loads(json_string)
        except Exception as error:
            logger.error(f"{agent_name} JSON Parse Error: {error}")
            logger.error(f"Raw response: {response}")
            raise ValueError(f"Failed to parse JSON response from {agent_name}: {error}")

    async def call_openai_image(self, prompt: str, system_prompt: str, data_url=None) -> str:
        logger.info(f"in call_openai_image with data_url")
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": f"{system_prompt}\n\n{prompt}"},
                    {"type": "image_url", "image_url": {"url": data_url}},
                ],
            }
        ]
        return self.client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.7
        )

    async def call_openai(self, prompt: str, system_prompt: str, data_url=None) -> str:
        logger.info(f"in call_openai without data_url")
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
        return self.client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            temperature=0.7
        )

    async def call_gemini(self, prompt: str, system_prompt: str, image_file) -> str:
        full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
        return self.model.generate_content(
            Part.from_text(full_prompt),
            Part.from_url(image_file, mime_type="image/png") if image_file else None,
            generation_config=genai.types.GenerationConfig(
                temperature=0.7
            )
        )

    async def call_llm(self, prompt: str, system_prompt: str = '', image: bytes = None) -> str:
        try :
            if model == "openai":
                if image:
                    base64_image = base64.b64encode(image).decode("utf-8")
                    image_url = f"data:image/png;base64,{base64_image}"
                    return await self.call_openai_image(prompt, system_prompt, image_url)
                else:
                    return await self.call_openai(prompt, system_prompt)
            elif model == "gemini":
                if image:
                    image_file = BytesIO(image)
                return await self.call_gemini(prompt, system_prompt, image_file)
        except Exception as e:
            logger.error(f"Error calling LLM: {str(e)}")
            raise e

    def extract_and_format_response(self, chat_completion_str):
        """
        Extract HTML from ChatCompletion response and format it properly
        """
        try:
            # If it's a ChatCompletion object (not a string), extract the content
            if hasattr(chat_completion_str, 'choices'):
                content = chat_completion_str.choices[0].message.content
                logger.info(f"in extract_and_format_response fetching content :: {content}")
            else:
                # It's a string representation, extract the content part
                content_match = re.search(r"content='(.*?)', refusal=", chat_completion_str, re.DOTALL)
                if content_match:
                    content = content_match.group(1)
                    # Unescape the string representation
                    content = content.encode().decode('unicode_escape')
                else:
                    content = chat_completion_str

            # Find the JSON block within the content
            json_match = re.search(r'```json\n(.*?)\n```', content, re.DOTALL)

            if not json_match:
                data = json.loads(content)
            else:
                json_content = json_match.group(1)
                logger.info(f"in extract_and_format_response fetching json_content ::  {json_content}")

                # Parse the JSON
                data = json.loads(json_content)

                # Extract the HTML code
                html_code = data.get('htmlCode', '')
                css_code = data.get('cssCode', '')
                logger.info(f"in extract_and_format_html :: html_code :: {html_code}")
                logger.info(f"in extract_and_format_html :: css_code :: {css_code}")

                if not html_code:
                    raise ValueError("No htmlCode found in the JSON")

            output_data = {
                "data": data
            }
            logger.info(f"in extract_and_format_response fetching output_data ::{output_data}")
            return output_data

        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON: {e}")
        except Exception as e:
            raise ValueError(f"Error processing response: {e}")

    async def image_agent_generate_html(self, user_prompt: str, image) -> Dict[str, Any]:
        prompt_file = Path(__file__).parent.parent / "prompts" / "image_prompt.txt"
        with open(prompt_file, 'r') as f:
            system_prompt = f.read()

        # Load system prompt
        prompt = f"""USER REQUIREMENT: {user_prompt}
        Analyze this UI and generate the code."""
        logger.info("Sending image bytes to llm")
        logger.info(f"model received: {model}")
        response = await self.call_llm(prompt, system_prompt, image)
        logger.info("in image_agent_generate_html calling extract html method")
        response = self.extract_and_format_response(response)
        logger.info(f"in image_agent_generate_html fetching response :: {response}")
        #return self.parse_json_response(response, 'Image Agent')
        return response['data'] if 'data' in response else response

    async def agent1_requirements_and_sling_model(self, user_prompt: str) -> Dict[str, Any]:
        prompt_file = Path(__file__).parent.parent / "prompts" / "agent_1.txt"
        with open(prompt_file, 'r') as f:
            system_prompt = f.read()

        # Load system prompt
        prompt = f"""USER REQUIREMENT: {user_prompt}
        Generate the complete analysis and Sling Model as specified."""

        response = await self.call_llm(prompt, system_prompt)
        logger.info(f"in agent1_requirements_and_sling_model fetching response :: {response}")
        response = self.extract_and_format_response(response)
        logger.info(f"in agent1_requirements_and_sling_model fetching response after extraction :: {response}")
        #return self.parse_json_response(response, 'Agent 1')
        return response['data'] if 'data' in response else response

    async def agent2_htl_generator(self, shared_context: Dict[str, Any], sling_model: str) -> Dict[str, Any]:
        prompt_file = Path(__file__).parent.parent / "prompts" / "agent_2.txt"
        with open(prompt_file, 'r') as f:
            system_prompt = f.read()

        # Load system prompt
        prompt = f"""SHARED CONTEXT: {json.dumps(shared_context, indent=2)}
        SLING MODEL REFERENCE: {sling_model}
        Generate the complete HTL template as specified.
        Given an AI agent has analyzed the image uploaded for the design and provided with the html and css code, generate the HTL template for the AEM component."""

        response = await self.call_llm(prompt, system_prompt)
        response = self.extract_and_format_response(response)
        #return self.parse_json_response(response, 'Agent 2')
        return response['data'] if 'data' in response else response

    async def agent3_dialog_generator(self, shared_context: Dict[str, Any], sling_model: str) -> Dict[str, Any]:
        prompt_file = Path(__file__).parent.parent / "prompts" / "agent_3.txt"
        with open(prompt_file, 'r') as f:
            system_prompt = f.read()

        # Load system prompt
        prompt = f"""SHARED CONTEXT: {json.dumps(shared_context, indent=2)}
        SLING MODEL REFERENCE: {sling_model}
        Generate the complete dialog configuration as specified."""

        response = await self.call_llm(prompt, system_prompt)
        response = self.extract_and_format_response(response)
        #return self.parse_json_response(response, 'Agent 3')
        return response['data'] if 'data' in response else response

    async def agent4_client_lib_generator(self, shared_context: Dict[str, Any], htl: str) -> Dict[str, Any]:
        prompt_file = Path(__file__).parent.parent / "prompts" / "agent_4.txt"
        with open(prompt_file, 'r') as f:
            system_prompt = f.read()

        # Load system prompt
        prompt = f"""SHARED CONTEXT: {json.dumps(shared_context, indent=2)}
        HTL REFERENCE: {htl}
        Generate the complete client library structure as specified."""

        response = await self.call_llm(prompt, system_prompt)
        response = self.extract_and_format_response(response)
        #return self.parse_json_response(response, 'Agent 4')
        return response['data'] if 'data' in response else response

    async def generate_aem_component(self, user_prompt: str, image) -> Dict[str, Any]:
        """Main orchestrator method with parallel execution"""
        logger.info('Starting AEM Component Generation...')
        try:
            logger.info('Starting AEM Component Generation...')
            image_gen_result = None
            if image:
                logger.info(f"Received data URL for image: {image[:50]}...")
                image_gen_result = await self.image_agent_generate_html(user_prompt, image)
                logger.info(f"Image generation result: {image_gen_result}")
            else:
                logger.info("No data URL provided for image.")

            # Agent 1: Requirements Analysis & Sling Model
            logger.info('Agent 1: Analyzing requirements and generating Sling Model...')
            agent1_result = await self.agent1_requirements_and_sling_model(user_prompt)
            logger.info(f'Agent 1: fetching agent1_result{agent1_result}')

            if 'sharedContext' not in agent1_result or 'slingModel' not in agent1_result:
                raise ValueError('Agent 1 failed to generate required outputs')

            # If image was provided, merge its results into shared context
            if image_gen_result:
                agent1_result['sharedContext'].update(image_gen_result)

            logger.info(f'Agent 1: fetching sharedContext{agent1_result['sharedContext']}')

            # Agents 2 & 3: Can run in parallel
            logger.info('Agent 2 & 3: Generating HTL and Dialog in parallel...')
            agent2_task = self.agent2_htl_generator(agent1_result['sharedContext'], agent1_result['slingModel'])
            agent3_task = self.agent3_dialog_generator(agent1_result['sharedContext'], agent1_result['slingModel'])

            agent2_result, agent3_result = await asyncio.gather(agent2_task, agent3_task)

            logger.info(f'Agent 3: fetching agent3_result{agent3_result}')

            if 'htl' not in agent2_result or 'dialog' not in agent3_result:
                raise ValueError('Agent 2 or 3 failed to generate required outputs')

            # Agent 4: Client Library (needs HTL from Agent 2)
            logger.info('Agent 4: Generating Client Library...')
            agent4_result = await self.agent4_client_lib_generator(
                agent1_result['sharedContext'],
                agent2_result['htl']
            )

            if 'clientLib' not in agent4_result:
                raise ValueError('Agent 4 failed to generate required outputs')

            # Combine final results
            final_result = {
                'htl': agent2_result['htl'],
                'slingModel': agent1_result['slingModel'],
                'dialog': agent3_result['dialog'],
                'content_xml': agent3_result['.content.xml'],
                'clientLib': agent4_result['clientLib']
            }

            logger.info('AEM Component Generation completed successfully!')
            return final_result

        except Exception as error:
            logger.error(f'AEM Component Generation failed: {error}')
            raise error

    async def generate_component(self, prompt: str, app_id: str, package: str, image) -> Dict[str, Any]:

        logger.info(f"In ComponentService generate_component :: {prompt}")

        try:
            component_data = await self.generate_aem_component(prompt, image)

            #ai_output = response.choices[0].message.content
            logger.info(f"In ComponentService ai_output :: {component_data}")

            try:
                # Parse AI response as JSON
                #component_data = json.loads(ai_output)
                logger.info(f"In ComponentService parsed component_data :: {component_data}")

                # Validate required keys
                if not all(key in component_data for key in ['slingModel', 'htl', 'dialog']):
                    raise ValueError('Incomplete AI output keys received')

            except (json.JSONDecodeError, ValueError) as json_err:
                logger.error(f"❌ Failed to parse AI response as JSON. Content was: {component_data}")
                raise json_err

            # Generate sanitized component name (similar to JavaScript version)
            sanitized_component_name = re.sub(r'[^a-z0-9_\-]', '_', app_id.lower())
            sanitized_component_name += "_" + "component"

            # Create actual files in the output directory
            output_dirs = self._create_component_files(component_data, app_id, package, sanitized_component_name)

            return {
                "success": True,
                "message": "✅ Component generated successfully.",
                "outputDirs": output_dirs,
                "structure": self._create_folder_structure(app_id, sanitized_component_name),
                "aiOutput": component_data
            }

        except Exception as e:
            logger.error(f"Component generation failed: {str(e)}")
            return {"success": False, "error": "Component generation failed.", "details": str(e)}

    def _create_component_files(self, component_data: Dict, app_id: str, package: str, component_name: str) -> Dict[str, str]:
        """Create actual files in the filesystem similar to JavaScript version"""

        # Prepare sanitized names and paths
        pkg_path = package.replace(".", "/")

        # Define output paths aligned with Maven archetype structure
        base_output_dir = Path(__file__).parent.parent.parent.parent / "output" / app_id

        sling_model_dir = base_output_dir / "core" / "src" / "main" / "java" / pkg_path / "core" / "models"
        ui_apps_dir = base_output_dir / "ui.apps" / "src" / "main" / "content" / "jcr_root" / "apps" / app_id / "components" / component_name
        ui_apps_clientlib_dir = base_output_dir / "ui.apps" / "src" / "main" / "content" / "jcr_root" / "apps" / app_id / "components" / component_name / "clientlib"
        ui_apps_clientlib_js_dir = ui_apps_clientlib_dir / "js"
        ui_apps_clientlib_css_dir = ui_apps_clientlib_dir / "css"

        # Ensure all directories exist (equivalent to fs.ensureDir in JavaScript)
        base_output_dir.mkdir(parents=True, exist_ok=True)
        sling_model_dir.mkdir(parents=True, exist_ok=True)
        ui_apps_dir.mkdir(parents=True, exist_ok=True)
        ui_apps_clientlib_dir.mkdir(parents=True, exist_ok=True)
        ui_apps_clientlib_js_dir.mkdir(parents=True, exist_ok=True)
        ui_apps_clientlib_css_dir.mkdir(parents=True, exist_ok=True)

        # Helper function to process content and convert escaped newlines to actual newlines
        def process_file_content(content: str) -> str:
            """Convert escaped newlines and other escape sequences to actual characters"""
            if isinstance(content, str):
                # Replace escaped newlines with actual newlines
                content = content.replace('\\n', '\n')
                # Replace escaped tabs with actual tabs
                content = content.replace('\\t', '\t')
                # Replace escaped quotes
                content = content.replace('\\"', '"')
                content = content.replace("\\'", "'")
                # Replace escaped backslashes
                content = content.replace('\\\\', '\\')
            return content

        # Helper function to fix common Java import and annotation issues
        def fix_java_code_issues(java_content: str) -> str:
            """Fix common issues in AI-generated Java code"""
            if not java_content:
                return java_content
            
            # Fix incorrect InjectionStrategy import
            java_content = java_content.replace(
                'import org.apache.sling.models.annotations.InjectionStrategy;',
                'import org.apache.sling.models.annotations.injectorspecific.InjectionStrategy;'
            )
            
            # Replace deprecated injection pattern with modern pattern
            import re
            java_content = re.sub(
                r'@ValueMapValue\(injectionStrategy\s*=\s*InjectionStrategy\.OPTIONAL\)',
                '@ValueMapValue\n    @Optional',
                java_content
            )
            
            # Add missing imports if they're used but not imported
            missing_imports = []
            if 'ArrayList' in java_content and 'import java.util.ArrayList;' not in java_content:
                missing_imports.append('import java.util.ArrayList;')
            if '@Optional' in java_content and 'import org.apache.sling.models.annotations.Optional;' not in java_content:
                missing_imports.append('import org.apache.sling.models.annotations.Optional;')
            if 'List<' in java_content and 'import java.util.List;' not in java_content:
                missing_imports.append('import java.util.List;')
            
            # Insert missing imports after package declaration
            if missing_imports:
                package_line_match = re.search(r'(package\s+[^;]+;)', java_content)
                if package_line_match:
                    package_line = package_line_match.group(1)
                    imports_text = '\n' + '\n'.join(missing_imports)
                    java_content = java_content.replace(package_line, package_line + imports_text)
            
            return java_content

        # Extract component name from shared context and create proper class name
        shared_context = component_data.get('sharedContext', {})
        component_display_name = shared_context.get('componentName', component_name)
        
        # Create proper class name from component name (e.g., "feature-grid" -> "FeatureGrid")
        class_name = self._create_class_name_from_component_name(component_display_name)
        
        # Write Sling Model Java class with proper class name
        java_file_path = sling_model_dir / f"{class_name}.java"
        java_content = process_file_content(component_data['slingModel'])
        
        # Fix class name in the Java content to match filename
        java_content = self._fix_class_name_in_java_content(java_content, class_name)
        java_content = fix_java_code_issues(java_content)
        
        with open(java_file_path, 'w', encoding='utf-8') as f:
            f.write(java_content)
        logger.info(f"Created Sling Model: {java_file_path} with class name: {class_name}")

        # Write .content.xml file directly from AI output
        content_xml_file_path = ui_apps_dir / f".content.xml"
        with open(content_xml_file_path, 'w', encoding='utf-8') as f:
            f.write(process_file_content(component_data['content_xml']))

        htl_file_path = ui_apps_dir / "component.html"
        with open(htl_file_path, 'w', encoding='utf-8') as f:
            f.write(process_file_content(component_data['htl']))

        dialog_file_path = ui_apps_dir / "_cq_dialog.xml"
        with open(dialog_file_path, 'w', encoding='utf-8') as f:
            f.write(process_file_content(component_data['dialog']))

        # Handle clientlib files with consistent format
        if 'clientLib' in component_data:
            logger.info("found clientLib in component_data")
            clientlib_data = component_data['clientLib']
            logger.info(f"after fetching clientLib data :: {clientlib_data}")

            # Handle each file in clientLib
            for file_path, file_data in clientlib_data.items():
                # Extract file content based on structure
                if isinstance(file_data, dict) and 'fileContents' in file_data:
                    content = file_data['fileContents']
                elif isinstance(file_data, str):
                    content = file_data
                else:
                    logger.warning(f"Unexpected file data format for {file_path}: {file_data}")
                    continue

                # Process content to convert escaped characters
                content = process_file_content(content)

                # Determine target directory and write file
                if file_path == 'js.txt':
                    target_path = ui_apps_clientlib_dir / "js.txt"
                elif file_path == 'css.txt':
                    target_path = ui_apps_clientlib_dir / "css.txt"
                elif file_path == '.content.xml':
                    target_path = ui_apps_clientlib_dir / ".content.xml"
                elif file_path.startswith('js/') and file_path.endswith('.js'):
                    filename = file_path.split('/')[-1]
                    target_path = ui_apps_clientlib_js_dir / filename
                elif file_path.startswith('css/') and file_path.endswith('.css'):
                    filename = file_path.split('/')[-1]
                    target_path = ui_apps_clientlib_css_dir / filename
                elif file_path.endswith('.js'):
                    target_path = ui_apps_clientlib_js_dir / file_path
                elif file_path.endswith('.css'):
                    target_path = ui_apps_clientlib_css_dir / file_path
                else:
                    logger.warning(f"Unknown file type: {file_path}")
                    continue

                # Write the file
                with open(target_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                logger.info(f"Created file: {target_path}")

        logger.info(f"✅ Files created successfully in {base_output_dir}")

        return {
            "coreJavaDir": str(sling_model_dir),
            "uiAppsDir": str(ui_apps_dir)
        }

    def _create_class_name_from_component_name(self, component_name: str) -> str:
        """Convert component name to proper Java class name (PascalCase)"""
        if not component_name:
            return "ComponentModel"
        
        # Remove common suffixes and clean the name
        cleaned_name = component_name.lower()
        cleaned_name = re.sub(r'[^a-zA-Z0-9\s\-_]', '', cleaned_name)
        
        # Split by common delimiters and convert to PascalCase
        words = re.split(r'[\s\-_]+', cleaned_name)
        class_name = ''.join(word.capitalize() for word in words if word)
        
        # Ensure it doesn't end with "Model" already, if not add it
        if not class_name.endswith('Model'):
            class_name += 'Model'
            
        return class_name

    def _fix_class_name_in_java_content(self, java_content: str, correct_class_name: str) -> str:
        """Fix the class name in Java content to match the filename"""
        if not java_content or not correct_class_name:
            return java_content
        
        # Pattern to match class declaration
        class_pattern = r'public\s+class\s+(\w+)\s*{'
        match = re.search(class_pattern, java_content)
        
        if match:
            old_class_name = match.group(1)
            # Replace the class name in the declaration
            java_content = re.sub(
                r'public\s+class\s+' + re.escape(old_class_name) + r'\s*{',
                f'public class {correct_class_name} {{',
                java_content
            )
            logger.info(f"Fixed class name from '{old_class_name}' to '{correct_class_name}'")
        else:
            logger.warning(f"Could not find class declaration in Java content to fix class name")
        
        return java_content

    def _create_folder_structure(self, app_id: str, component_name: str) -> Dict[str, Any]:
        return {
            "name": f"output/{app_id}",
            "type": "folder",
            "children": [
                {
                    "name": "core",
                    "type": "folder",
                    "children": [
                        {
                            "name": "src/main/java",
                            "type": "folder",
                            "children": [
                                {
                                    "name": f"{component_name}.java",
                                    "type": "file"
                                }
                            ]
                        }
                    ]
                },
                {
                    "name": "ui.apps",
                    "type": "folder",
                    "children": [
                        {
                            "name": f"src/main/content/jcr_root/apps/{app_id}/components/{component_name}",
                            "type": "folder",
                            "children": [
                                {"name": "component.html", "type": "file"},
                                {"name": "_cq_dialog.xml", "type": "file"}
                            ]
                        }
                    ]
                }
            ]
        }