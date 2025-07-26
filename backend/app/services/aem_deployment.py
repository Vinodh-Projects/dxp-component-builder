"""
AEM Deployment Service - Handles building and deploying AEM projects to AEM Author server
"""

import asyncio
import subprocess
import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import shutil
import aiohttp
import ssl

logger = logging.getLogger(__name__)

class AEMDeploymentService:
    """Service to build and deploy AEM projects to AEM Author server"""
    
    def __init__(self):
        # Use relative import to avoid circular import issues
        try:
            from ..config import settings
            self.project_root = Path(settings.PROJECT_CODE_PATH)
            self.aem_server_url = settings.AEM_AUTHOR_URL
            self.aem_username = settings.AEM_USERNAME
            self.aem_password = settings.AEM_PASSWORD
            self.maven_profiles = settings.MAVEN_PROFILES
            self.skip_tests = settings.SKIP_TESTS
            self.mock_mode = settings.AEM_MOCK_MODE
        except ImportError:
            # Fallback values
            self.project_root = Path("/app/project_code")
            self.aem_server_url = "http://localhost:4502"
            self.aem_username = "admin"
            self.aem_password = "admin"
            self.maven_profiles = "adobe-public,autoInstallPackage"
            self.skip_tests = True
            self.mock_mode = True
    
    async def build_and_deploy_project(self) -> Dict[str, Any]:
        """
        Build and deploy the entire AEM project
        
        Returns:
            Result dictionary with build and deployment status
        """
        try:
            logger.info(f"Starting build and deployment process for project: {self.project_root}")
            
            # Step 1: Validate project structure
            validation_result = await self._validate_project_structure()
            if not validation_result["valid"]:
                return {
                    "success": False,
                    "message": "Project validation failed",
                    "error": validation_result["error"],
                    "step": "validation"
                }
            
            # Step 2: Clean and build project
            build_result = await self._build_project()
            if not build_result["success"]:
                return {
                    "success": False,
                    "message": "Project build failed",
                    "error": build_result["error"],
                    "step": "build",
                    "build_log": build_result.get("log")
                }
            
            # Step 3: Deploy to AEM
            deploy_result = await self._deploy_to_aem()
            if not deploy_result["success"]:
                return {
                    "success": False,
                    "message": "AEM deployment failed",
                    "error": deploy_result["error"],
                    "step": "deployment",
                    "deploy_log": deploy_result.get("log")
                }
            
            result = {
                "success": True,
                "message": "Successfully built and deployed AEM project",
                "project_path": str(self.project_root),
                "aem_server": self.aem_server_url,
                "build_time": build_result.get("duration"),
                "deploy_time": deploy_result.get("duration"),
                "deployed_packages": deploy_result.get("packages", []),
                "deployed_at": datetime.now().isoformat()
            }
            
            logger.info("Build and deployment completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Build and deployment failed: {str(e)}")
            return {
                "success": False,
                "message": f"Build and deployment failed: {str(e)}",
                "error": str(e),
                "step": "general"
            }
    
    async def _validate_project_structure(self) -> Dict[str, Any]:
        """Validate AEM project structure"""
        try:
            # First check if Maven is available
            try:
                result = subprocess.run(["mvn", "--version"], capture_output=True, check=True, text=True)
                logger.info(f"Maven version: {result.stdout.split()[2] if result.stdout else 'Unknown'}")
            except (subprocess.CalledProcessError, FileNotFoundError) as e:
                logger.error(f"Maven not available: {str(e)}")
                return {
                    "valid": False,
                    "error": "Maven is not installed or not available in PATH. Please install Maven to use AEM deployment features."
                }

            # Check if project root exists
            if not self.project_root.exists():
                logger.error(f"Project root does not exist: {self.project_root}")
                return {
                    "valid": False,
                    "error": f"Project root directory does not exist: {self.project_root}"
                }

            # Check for essential files (ui.apps is minimum requirement)
            essential_files = [
                "pom.xml",
                "ui.apps/pom.xml"
            ]
            
            missing_files = []
            for file_path in essential_files:
                full_path = self.project_root / file_path
                if not full_path.exists():
                    missing_files.append(file_path)
                    logger.warning(f"Missing file: {full_path}")
            
            if missing_files:
                return {
                    "valid": False,
                    "error": f"Missing required files: {', '.join(missing_files)}. Please ensure you have a valid AEM Maven project structure."
                }

            logger.info("Project structure validation passed")
            return {"valid": True}
            
        except Exception as e:
            logger.error(f"Project validation failed: {str(e)}")
            return {
                "valid": False,
                "error": f"Validation error: {str(e)}"
            }
    
    async def _build_project(self) -> Dict[str, Any]:
        """Build the AEM project using Maven"""
        try:
            start_time = datetime.now()
            
            # Construct Maven command
            maven_cmd = [
                "mvn",
                "clean",
                "install",
                f"-P{self.maven_profiles}"
            ]
            
            if self.skip_tests:
                maven_cmd.append("-DskipTests")
            
            logger.info(f"Running Maven build: {' '.join(maven_cmd)}")
            
            # Run Maven build
            process = await asyncio.create_subprocess_exec(
                *maven_cmd,
                cwd=self.project_root,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT
            )
            
            stdout, _ = await process.communicate()
            build_log = stdout.decode('utf-8')
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            if process.returncode == 0:
                logger.info(f"Maven build completed successfully in {duration:.2f} seconds")
                return {
                    "success": True,
                    "duration": duration,
                    "log": build_log
                }
            else:
                logger.error(f"Maven build failed with return code {process.returncode}")
                return {
                    "success": False,
                    "error": f"Maven build failed with return code {process.returncode}",
                    "log": build_log
                }
                
        except Exception as e:
            logger.error(f"Build process failed: {str(e)}")
            return {
                "success": False,
                "error": f"Build process failed: {str(e)}"
            }

    async def simple_build_and_deploy(self) -> Dict[str, Any]:
        """
        Simple build and deploy using mvn clean install -PautoInstallPackage -DskipTests -Padobe-public
        This method directly runs the Maven command that builds and deploys in one step
        """
        try:
            start_time = datetime.now()
            
            # Your requested Maven command
            maven_cmd = [
                "mvn",
                "clean", 
                "install",
                "-PautoInstallPackage",
                "-DskipTests",
                "-Padobe-public"
            ]
            
            logger.info(f"Running simple build and deploy: {' '.join(maven_cmd)}")
            logger.info(f"Working directory: {self.project_root}")
            
            # Run Maven command
            process = await asyncio.create_subprocess_exec(
                *maven_cmd,
                cwd=self.project_root,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT
            )
            
            # Capture output and log it in real-time
            output_lines = []
            if process.stdout:
                while True:
                    line = await process.stdout.readline()
                    if not line:
                        break
                    line_str = line.decode('utf-8').rstrip()
                    output_lines.append(line_str)
                    # Log Maven output in real-time
                    logger.info(f"Maven: {line_str}")
            
            await process.wait()
            build_log = '\n'.join(output_lines)
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            if process.returncode == 0:
                logger.info(f"Simple build and deploy completed successfully in {duration:.2f} seconds")
                
                # Extract deployed packages from log if possible
                deployed_packages = []
                if "BUILD SUCCESS" in build_log:
                    # Look for package installation messages in the log
                    lines = build_log.split('\n')
                    for line in lines:
                        if "Installing package" in line or "Installed package" in line:
                            # Extract package name from log line
                            parts = line.split()
                            for part in parts:
                                if part.endswith('.zip'):
                                    deployed_packages.append(part)
                
                return {
                    "success": True,
                    "message": "Build and deploy completed successfully",
                    "duration": duration,
                    "build_log": build_log,
                    "deployed_packages": deployed_packages,
                    "aem_server": self.aem_server_url,
                    "project_path": str(self.project_root),
                    "maven_command": ' '.join(maven_cmd),
                    "completed_at": datetime.now().isoformat()
                }
            else:
                logger.error(f"Simple build and deploy failed with return code {process.returncode}")
                return {
                    "success": False,
                    "message": "Build and deploy failed",
                    "error": f"Maven command failed with return code {process.returncode}",
                    "duration": duration,
                    "build_log": build_log,
                    "maven_command": ' '.join(maven_cmd),
                    "failed_at": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Simple build and deploy process failed: {str(e)}")
            return {
                "success": False,
                "message": "Build and deploy process failed",
                "error": f"Process failed: {str(e)}",
                "maven_command": ' '.join(maven_cmd) if 'maven_cmd' in locals() else "Command not initialized"
            }
    
    async def _deploy_to_aem(self) -> Dict[str, Any]:
        """Deploy built packages to AEM Author server"""
        try:
            start_time = datetime.now()
            deployed_packages = []
            
            # Find all built packages
            package_paths = list(self.project_root.glob("**/target/*.zip"))
            all_package_path = None
            
            # Look for the 'all' package specifically
            for package_path in package_paths:
                if "all" in package_path.parent.parent.name.lower():
                    all_package_path = package_path
                    break
            
            if not all_package_path:
                # If no 'all' package found, look for any .zip package
                if package_paths:
                    all_package_path = package_paths[0]
                else:
                    return {
                        "success": False,
                        "error": "No deployment packages found. Build may have failed."
                    }
            
            logger.info(f"Deploying package: {all_package_path}")
            
            # Deploy using curl (AEM Package Manager API)
            curl_cmd = [
                "curl",
                "-u", f"{self.aem_username}:{self.aem_password}",
                "-F", f"file=@{all_package_path}",
                "-F", "force=true",
                "-F", "install=true",
                f"{self.aem_server_url}/crx/packmgr/service.jsp"
            ]
            
            process = await asyncio.create_subprocess_exec(
                *curl_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT
            )
            
            stdout, _ = await process.communicate()
            deploy_log = stdout.decode('utf-8')
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            if process.returncode == 0 and "success" in deploy_log.lower():
                deployed_packages.append(str(all_package_path.name))
                logger.info(f"Package deployed successfully in {duration:.2f} seconds")
                return {
                    "success": True,
                    "duration": duration,
                    "packages": deployed_packages,
                    "log": deploy_log
                }
            else:
                logger.error(f"Package deployment failed")
                return {
                    "success": False,
                    "error": "Package deployment failed",
                    "log": deploy_log
                }
                
        except Exception as e:
            logger.error(f"Deployment process failed: {str(e)}")
            return {
                "success": False,
                "error": f"Deployment process failed: {str(e)}"
            }
    
    async def get_deployment_status(self) -> Dict[str, Any]:
        """Get current deployment status from AEM server"""
        try:
            # Convert internal Docker URL to public URL for frontend display
            display_url = self.aem_server_url.replace("host.docker.internal", "localhost")
            
            # In mock mode, return successful status for development
            if self.mock_mode:
                return {
                    "server_available": True,
                    "server_url": display_url,
                    "response": "Mock AEM server - development mode",
                    "message": "AEM server status check completed"
                }
            
            # Check AEM server health using HTTP client instead of curl
            try:
                logger.info(f"Checking AEM health at: {self.aem_server_url}")
                
                auth = aiohttp.BasicAuth(self.aem_username, self.aem_password)
                # Create SSL context that doesn't verify certificates (for local development)
                ssl_context = ssl.create_default_context()
                ssl_context.check_hostname = False
                ssl_context.verify_mode = ssl.CERT_NONE
                
                timeout = aiohttp.ClientTimeout(total=10)  # 10 second timeout
                
                async with aiohttp.ClientSession(auth=auth, timeout=timeout, connector=aiohttp.TCPConnector(ssl=ssl_context)) as session:
                    # Use internal URL for actual connection, display_url for user display only
                    async with session.get(f"{self.aem_server_url}/libs/granite/core/content/login.html") as response:
                        logger.info(f"AEM health check: status={response.status}")
                        
                        if response.status == 200:
                            return {
                                "server_available": True,
                                "server_url": display_url,
                                "response": f"AEM server is accessible (HTTP {response.status})",
                                "message": "AEM server status check completed"
                            }
                        else:
                            return {
                                "server_available": False,
                                "server_url": display_url,
                                "error": f"AEM server not accessible (HTTP {response.status})",
                                "message": "AEM server status check completed"
                            }
                            
            except Exception as http_e:
                logger.error(f"HTTP health check failed: {str(http_e)}")
                return {
                    "server_available": False,
                    "server_url": display_url,
                    "error": f"Unable to connect to AEM server: {str(http_e)}",
                    "message": "AEM server status check completed"
                }
                
        except Exception as e:
            logger.error(f"Status check failed: {str(e)}")
            # Convert internal Docker URL to public URL for frontend display
            display_url = self.aem_server_url.replace("host.docker.internal", "localhost")
            return {
                "server_available": False,
                "server_url": display_url,
                "error": str(e),
                "message": "AEM server status check completed"
            }
    
    async def build_specific_module(self, module_name: str) -> Dict[str, Any]:
        """Build and deploy a specific module"""
        try:
            module_path = self.project_root / module_name
            if not module_path.exists():
                return {
                    "success": False,
                    "error": f"Module '{module_name}' not found"
                }
            
            start_time = datetime.now()
            
            # Build specific module
            maven_cmd = [
                "mvn",
                "clean",
                "install",
                f"-P{self.maven_profiles}"
            ]
            
            if self.skip_tests:
                maven_cmd.append("-DskipTests")
            
            process = await asyncio.create_subprocess_exec(
                *maven_cmd,
                cwd=module_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT
            )
            
            stdout, _ = await process.communicate()
            build_log = stdout.decode('utf-8')
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            if process.returncode == 0:
                return {
                    "success": True,
                    "module": module_name,
                    "duration": duration,
                    "message": f"Module '{module_name}' built and deployed successfully",
                    "log": build_log
                }
            else:
                return {
                    "success": False,
                    "module": module_name,
                    "error": f"Module build failed with return code {process.returncode}",
                    "log": build_log
                }
                
        except Exception as e:
            logger.error(f"Module build failed: {str(e)}")
            return {
                "success": False,
                "module": module_name,
                "error": str(e)
            }
    
    async def _test_aem_connectivity(self) -> bool:
        """Test connectivity to AEM server"""
        try:
            # In mock mode, always return success for development
            if self.mock_mode:
                return True
                
            curl_cmd = [
                "curl",
                "-u", f"{self.aem_username}:{self.aem_password}",
                "-s",
                "--connect-timeout", "10",
                f"{self.aem_server_url}/libs/granite/core/content/login.html"
            ]
            
            process = await asyncio.create_subprocess_exec(
                *curl_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT
            )
            
            stdout, _ = await process.communicate()
            return process.returncode == 0
            
        except Exception as e:
            logger.error(f"AEM connectivity test failed: {str(e)}")
            return False
    
    async def _build_specific_module(self, module_name: str) -> Dict[str, Any]:
        """Build a specific module using Maven"""
        try:
            module_path = self.project_root / module_name
            
            maven_cmd = [
                "mvn",
                "clean",
                "install",
                f"-P{self.maven_profiles}"
            ]
            
            if self.skip_tests:
                maven_cmd.append("-DskipTests")
            
            process = await asyncio.create_subprocess_exec(
                *maven_cmd,
                cwd=module_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT
            )
            
            stdout, _ = await process.communicate()
            build_log = stdout.decode('utf-8')
            
            return {
                "success": process.returncode == 0,
                "output": build_log,
                "return_code": process.returncode
            }
            
        except Exception as e:
            logger.error(f"Module build failed: {str(e)}")
            return {
                "success": False,
                "output": str(e),
                "return_code": -1
            }
    
    async def _deploy_module_to_aem(self, module_name: str) -> Dict[str, Any]:
        """Deploy a specific module to AEM"""
        try:
            # Find the built package
            if module_name == "all":
                package_path = self.project_root / "all" / "target"
            elif module_name == "ui.apps":
                package_path = self.project_root / "ui.apps" / "target"
            elif module_name == "ui.content":
                package_path = self.project_root / "ui.content" / "target"
            else:
                return {
                    "success": False,
                    "output": f"Module '{module_name}' is not deployable"
                }
            
            # Find the zip package
            zip_packages = list(package_path.glob("*.zip"))
            if not zip_packages:
                return {
                    "success": False,
                    "output": f"No package found for module '{module_name}'"
                }
            
            package_file = zip_packages[0]  # Take the first zip file
            
            # Deploy using curl
            curl_cmd = [
                "curl",
                "-u", f"{self.aem_username}:{self.aem_password}",
                "-F", f"file=@{package_file}",
                "-F", "force=true",
                "-F", "install=true",
                f"{self.aem_server_url}/crx/packmgr/service.jsp"
            ]
            
            process = await asyncio.create_subprocess_exec(
                *curl_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT
            )
            
            stdout, _ = await process.communicate()
            deploy_log = stdout.decode('utf-8')
            
            success = process.returncode == 0 and "success" in deploy_log.lower()
            
            return {
                "success": success,
                "output": deploy_log,
                "package": str(package_file.name)
            }
            
        except Exception as e:
            logger.error(f"Module deployment failed: {str(e)}")
            return {
                "success": False,
                "output": str(e)
            }
