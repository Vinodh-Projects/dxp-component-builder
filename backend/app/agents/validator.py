# app/agents/validator.py
from typing import Dict, Any, List
from app.agents.base import BaseAgent
import re
import json

class ComponentValidator(BaseAgent):
    """Agent for validating generated AEM components"""
    
    def __init__(self):
        super().__init__("component_validator")
    
    def get_system_prompt(self) -> str:
        return """You are an AEM Component Quality Validator. Review the generated component for completeness and best practices.

VALIDATION CHECKLIST:
1. Code Completeness
   - No placeholders or TODO comments
   - All methods implemented
   - All required files present
   - Java class names match file names
   - Package declarations are consistent

2. AEM Best Practices
   - Proper resource types matching between @Model and content.xml
   - Correct annotations (@Model, @ValueMapValue, @Optional)
   - No deprecated injection strategies
   - Proper null handling and input validation
   - Consistent naming conventions

3. Compilation Safety
   - All required imports present
   - No missing dependencies
   - Proper syntax and balanced braces/parentheses
   - Getter methods for all @ValueMapValue fields
   - Valid HTL syntax and matched HTML tags

4. Performance
   - Lazy loading implemented
   - Efficient selectors
   - Optimized client libraries
   - Resource management (proper closing of ResourceResolver)

5. Accessibility
   - ARIA labels present
   - Semantic HTML
   - Keyboard navigation support
   - Screen reader compatibility
   - Proper form field labels

6. Security
   - XSS prevention (no unsafe innerHTML, eval, document.write)
   - Input validation
   - Safe resource handling
   - No hardcoded secrets or credentials
   - SQL injection prevention
   - Proper HTL output escaping

OUTPUT FORMAT:
{
  "validationStatus": "PASS/FAIL",
  "score": 0-100,
  "issues": ["list of critical issues that must be fixed"],
  "suggestions": ["list of improvements and best practices"],
  "details": {
    "completeness": 0-100,
    "bestPractices": 0-100,
    "performance": 0-100,
    "accessibility": 0-100,
    "security": 0-100
  }
}"""
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate generated component"""
        
        component_files = input_data.get('files', {})
        
        # Perform automated validation
        validation_result = await self._automated_validation(component_files)
        
        # If enabled, also use LLM for deeper validation
        if input_data.get('deep_validation', True):
            llm_validation = await self._llm_validation(component_files)
            validation_result = self._merge_validations(validation_result, llm_validation)
        
        return validation_result
    
    async def _automated_validation(self, files: Dict[str, Any]) -> Dict[str, Any]:
        """Perform automated code validation"""
        
        issues = []
        suggestions = []
        scores = {
            "completeness": 100,
            "bestPractices": 100,
            "performance": 100,
            "accessibility": 100,
            "security": 100
        }
        
        # Check for placeholders
        placeholder_patterns = [
            r'TODO',
            r'FIXME',
            r'// Add .* here',
            r'/\* .* code here \*/',
            r'\.\.\.',
            r'placeholder',
            r'implement here',
            r'fill in'
        ]
        
        for file_name, content in files.items():
            if isinstance(content, str):
                for pattern in placeholder_patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        issues.append(f"Placeholder or incomplete code found in {file_name}")
                        scores["completeness"] -= 15

        # Check for required files with more comprehensive validation
        required_files = ['slingModel', 'htl', 'dialog']
        missing_files = []
        for req_file in required_files:
            file_content = files.get(req_file)
            if not file_content or (isinstance(file_content, str) and not file_content.strip()):
                missing_files.append(req_file)
                scores["completeness"] -= 25

        if missing_files:
            issues.append(f"Missing or empty required files: {', '.join(missing_files)}")

        # Check Java class name and file name consistency
        if files.get('slingModel') and files.get('projectStructure', {}).get('slingModelPath'):
            java_issues = self._validate_java_class_consistency(
                files['slingModel'], 
                files['projectStructure']['slingModelPath']
            )
            issues.extend(java_issues)
            if java_issues:
                scores["bestPractices"] -= 20

        # Validate package declarations
        package_issues = self._validate_package_declarations(files)
        issues.extend(package_issues)
        if package_issues:
            scores["bestPractices"] -= 15

        # Check for compilation errors
        compilation_issues = self._check_compilation_errors(files)
        issues.extend(compilation_issues)
        if compilation_issues:
            scores["completeness"] -= 30

        # Enhanced vulnerability checks
        vulnerability_issues = self._check_security_vulnerabilities(files)
        issues.extend(vulnerability_issues)
        if vulnerability_issues:
            scores["security"] -= 25

        # Enhanced HTL validation
        htl_content = files.get('htl', '')
        if htl_content:
            htl_checks = 0
            if 'data-sly-use' in htl_content:
                htl_checks += 1
            else:
                issues.append("HTL missing data-sly-use directive for Sling Model integration")
                scores["bestPractices"] -= 15
            
            if re.search(r'aria-\w+', htl_content):
                htl_checks += 1
            else:
                suggestions.append("Add ARIA attributes for better accessibility")
                scores["accessibility"] -= 10
            
            if re.search(r'data-sly-test|data-sly-if', htl_content):
                htl_checks += 1
            else:
                suggestions.append("Consider adding conditional rendering with data-sly-test")
                scores["bestPractices"] -= 5
            
            if re.search(r'class=|id=', htl_content):
                htl_checks += 1
            else:
                suggestions.append("Add CSS classes for styling")
                scores["performance"] -= 5
            
            # Bonus points for good practices
            if htl_checks >= 3:
                scores["bestPractices"] += 5

        # Enhanced Sling Model validation
        sling_model = files.get('slingModel', '')
        if sling_model:
            model_checks = 0
            
            if '@Model' in sling_model:
                model_checks += 1
            else:
                issues.append("Sling Model missing @Model annotation")
                scores["bestPractices"] -= 20
            
            if '@Inject' in sling_model or '@ValueMapValue' in sling_model:
                model_checks += 1
            else:
                suggestions.append("Consider using dependency injection (@Inject, @ValueMapValue)")
                scores["bestPractices"] -= 10
            
            if 'StringUtils.isNotBlank' in sling_model or 'Optional' in sling_model or 'null' in sling_model:
                model_checks += 1
            else:
                issues.append("Missing null safety checks in Sling Model")
                scores["security"] -= 15
            
            if '@PostConstruct' in sling_model:
                model_checks += 1
                scores["bestPractices"] += 5
            
            if 'ResourceResolver' in sling_model and 'try-with-resources' not in sling_model:
                suggestions.append("Use try-with-resources for ResourceResolver")
                scores["security"] -= 10
            
            # Bonus for comprehensive models
            if model_checks >= 3:
                scores["completeness"] += 5

        # Dialog validation
        dialog_content = files.get('dialog', '')
        if dialog_content:
            if 'granite/ui/components' in dialog_content:
                scores["bestPractices"] += 5
            else:
                suggestions.append("Use Granite UI components in dialog")
                scores["bestPractices"] -= 10
            
            if 'fieldLabel' in dialog_content:
                scores["accessibility"] += 5
            else:
                suggestions.append("Add field labels for accessibility")
                scores["accessibility"] -= 10

        # Client libraries validation
        clientlibs = files.get('clientlibs', {})
        if isinstance(clientlibs, dict):
            css_content = clientlibs.get('css', '')
            js_content = clientlibs.get('js', '')
            
            if css_content:
                if 'responsive' in css_content or '@media' in css_content:
                    scores["accessibility"] += 5
                else:
                    suggestions.append("Consider responsive design in CSS")
                    scores["accessibility"] -= 5
                
                if 'focus' in css_content or ':hover' in css_content:
                    scores["accessibility"] += 5
                
            if js_content:
                if 'addEventListener' in js_content:
                    scores["bestPractices"] += 5
                
                if 'console.log' in js_content:
                    suggestions.append("Remove console.log statements in production code")
                    scores["performance"] -= 5

        # Security checks
        all_content = ' '.join([str(content) for content in files.values() if isinstance(content, str)])
        if 'innerHTML' in all_content:
            issues.append("Potential XSS vulnerability: avoid innerHTML")
            scores["security"] -= 20
        
        if 'eval(' in all_content:
            issues.append("Security risk: avoid eval() function")
            scores["security"] -= 25

        # Ensure scores don't go below 0 or above 100
        for key in scores:
            scores[key] = max(0, min(100, scores[key]))

        # Calculate weighted overall score
        weights = {
            "completeness": 0.3,
            "bestPractices": 0.25,
            "performance": 0.15,
            "accessibility": 0.15,
            "security": 0.15
        }
        
        overall_score = int(sum(scores[key] * weights[key] for key in scores))
        validation_status = "PASS" if overall_score >= 70 else "FAIL"

        return {
            "validationStatus": validation_status,
            "score": overall_score,
            "issues": issues,
            "suggestions": suggestions,
            "details": scores
        }
    
    async def _llm_validation(self, files: Dict[str, Any]) -> Dict[str, Any]:
        """Use LLM for deeper validation"""
        
        # Create a more detailed prompt based on the component content
        component_type = "unknown"
        if files.get('htl'):
            htl_content = files['htl'].lower()
            if 'button' in htl_content:
                component_type = "button"
            elif 'form' in htl_content or 'input' in htl_content:
                component_type = "form"
            elif 'image' in htl_content or 'img' in htl_content:
                component_type = "image"
            elif 'nav' in htl_content or 'menu' in htl_content:
                component_type = "navigation"
            elif 'text' in htl_content or 'content' in htl_content:
                component_type = "content"
        
        prompt = f"""You are an expert AEM developer reviewing a {component_type} component. Analyze the following files and provide a detailed validation:

FILES TO VALIDATE:
{json.dumps(files, indent=2)}

COMPONENT TYPE: {component_type}

Provide a comprehensive analysis focusing on:

1. **CODE COMPLETENESS** (0-100):
   - Are all methods fully implemented (no TODOs/placeholders)?
   - Are all required AEM files present and properly structured?
   - Do Java class names match file names?
   - Are package declarations consistent across files?
   - Is the component production-ready?

2. **AEM BEST PRACTICES** (0-100):
   - Proper use of Sling Models and annotations
   - Correct HTL templating practices
   - Appropriate dialog structure
   - Resource type naming conventions and consistency
   - Component categorization
   - No deprecated patterns (e.g., InjectionStrategy)

3. **COMPILATION SAFETY** (0-100):
   - All required imports present
   - No syntax errors or unmatched braces
   - Proper getter methods for @ValueMapValue fields
   - Valid HTL syntax
   - No missing dependencies

4. **PERFORMANCE** (0-100):
   - Efficient resource handling
   - Lazy loading implementation
   - Client library optimization
   - Caching considerations
   - Proper resource cleanup

5. **ACCESSIBILITY** (0-100):
   - WCAG 2.1 compliance
   - ARIA attributes and labels
   - Semantic HTML structure
   - Keyboard navigation support
   - Screen reader compatibility

6. **SECURITY** (0-100):
   - XSS prevention measures (no unsafe innerHTML, eval, etc.)
   - Input validation and sanitization
   - Safe resource handling
   - No hardcoded secrets
   - Proper HTL output escaping
   - SQL injection prevention

For a {component_type} component specifically, also check:
- Component-specific best practices
- User interaction patterns
- Data handling requirements

Respond in this EXACT JSON format:
{{
  "validationStatus": "PASS/FAIL",
  "score": 0-100,
  "issues": ["specific critical issues that must be fixed"],
  "suggestions": ["actionable improvements to enhance the component"],
  "details": {{
    "completeness": 0-100,
    "bestPractices": 0-100,
    "performance": 0-100,
    "accessibility": 0-100,
    "security": 0-100
  }},
  "componentTypeAnalysis": "specific analysis for {component_type} components"
}}

Be thorough and specific in your feedback. Provide different scores and feedback based on the actual code quality."""
        
        response = await self.call_gpt4(prompt)
        result = self.parse_json_response(response)
        
        # Add fallback values if LLM response is incomplete
        if not isinstance(result, dict):
            result = {}
        
        # Ensure all required fields are present
        result.setdefault('validationStatus', 'UNKNOWN')
        result.setdefault('score', 50)
        result.setdefault('issues', [])
        result.setdefault('suggestions', [])
        result.setdefault('details', {
            'completeness': 50,
            'bestPractices': 50,
            'performance': 50,
            'accessibility': 50,
            'security': 50
        })
        
        return result
    
    def _merge_validations(self, auto_result: Dict, llm_result: Dict) -> Dict:
        """Merge automated and LLM validation results"""
        
        # Combine issues and suggestions
        all_issues = list(set(auto_result.get('issues', []) + llm_result.get('issues', [])))
        all_suggestions = list(set(auto_result.get('suggestions', []) + llm_result.get('suggestions', [])))
        
        # Average the scores
        auto_score = auto_result.get('score', 0)
        llm_score = llm_result.get('score', 0)
        final_score = (auto_score + llm_score) // 2
        
        # Merge detail scores
        merged_details = {}
        for key in ['completeness', 'bestPractices', 'performance', 'accessibility', 'security']:
            auto_val = auto_result.get('details', {}).get(key, 0)
            llm_val = llm_result.get('details', {}).get(key, 0)
            merged_details[key] = (auto_val + llm_val) // 2
        
        return {
            "validationStatus": "PASS" if final_score >= 70 else "FAIL",
            "score": final_score,
            "issues": all_issues,
            "suggestions": all_suggestions,
            "details": merged_details
        }
    
    def _validate_java_class_consistency(self, java_content: str, file_path: str) -> List[str]:
        """Validate that Java class name matches the file name"""
        issues = []
        
        # Extract class name from Java content
        class_match = re.search(r'public\s+class\s+(\w+)', java_content)
        if not class_match:
            issues.append("No public class declaration found in Sling Model")
            return issues
        
        class_name = class_match.group(1)
        
        # Extract expected file name from path
        if file_path:
            expected_file_name = file_path.split('/')[-1].replace('.java', '')
            if class_name != expected_file_name:
                issues.append(f"Class name '{class_name}' does not match file name '{expected_file_name}.java'")
        
        # Check if class name follows naming conventions
        if not class_name.endswith('Model'):
            issues.append(f"Sling Model class '{class_name}' should end with 'Model' suffix")
        
        # Check if class name is PascalCase
        if not re.match(r'^[A-Z][a-zA-Z0-9]*$', class_name):
            issues.append(f"Class name '{class_name}' should be in PascalCase format")
        
        return issues
    
    def _validate_package_declarations(self, files: Dict[str, Any]) -> List[str]:
        """Validate package declarations consistency"""
        issues = []
        
        sling_model = files.get('slingModel', '')
        project_structure = files.get('projectStructure', {})
        
        if sling_model:
            # Extract package from Java code
            package_match = re.search(r'package\s+([^;]+);', sling_model)
            if not package_match:
                issues.append("Missing package declaration in Sling Model")
                return issues
            
            declared_package = package_match.group(1).strip()
            
            # Check if package follows expected structure
            if not declared_package.endswith('core.models'):
                issues.append(f"Package '{declared_package}' should end with '.core.models'")
            
            # Validate package path consistency
            sling_model_path = project_structure.get('slingModelPath', '')
            if sling_model_path:
                # Extract expected package from file path
                path_parts = sling_model_path.split('/')
                java_index = -1
                for i, part in enumerate(path_parts):
                    if part == 'java':
                        java_index = i
                        break
                
                if java_index >= 0 and java_index + 1 < len(path_parts):
                    package_path_parts = path_parts[java_index + 1:-1]  # Exclude file name
                    expected_package = '.'.join(package_path_parts)
                    
                    if declared_package != expected_package:
                        issues.append(f"Package declaration '{declared_package}' does not match file path '{expected_package}'")
        
        return issues
    
    def _check_compilation_errors(self, files: Dict[str, Any]) -> List[str]:
        """Check for potential Java compilation errors"""
        issues = []
        
        sling_model = files.get('slingModel', '')
        if sling_model:
            # Check for missing imports
            required_patterns = {
                '@Model': 'import org.apache.sling.models.annotations.Model;',
                '@ValueMapValue': 'import org.apache.sling.models.annotations.injectorspecific.ValueMapValue;',
                'Resource': 'import org.apache.sling.api.resource.Resource;',
                '@Optional': 'import org.apache.sling.models.annotations.Optional;',
                '@Default': 'import org.apache.sling.models.annotations.Default;',
                '@PostConstruct': 'import javax.annotation.PostConstruct;',
                'List<': 'import java.util.List;',
                'ArrayList': 'import java.util.ArrayList;'
            }
            
            for pattern, required_import in required_patterns.items():
                if pattern in sling_model and required_import not in sling_model:
                    issues.append(f"Missing import: {required_import}")
            
            # Check for deprecated injection strategy
            if 'InjectionStrategy.OPTIONAL' in sling_model:
                issues.append("Using deprecated InjectionStrategy.OPTIONAL - use @Optional annotation instead")
            
            # Check for proper @Model annotation
            if '@Model' in sling_model:
                if 'adaptables' not in sling_model or 'Resource.class' not in sling_model:
                    issues.append("@Model annotation should specify adaptables = Resource.class")
                
                if 'resourceType' not in sling_model:
                    issues.append("@Model annotation missing resourceType parameter")
            
            # Check for unmatched braces/parentheses
            open_braces = sling_model.count('{')
            close_braces = sling_model.count('}')
            if open_braces != close_braces:
                issues.append(f"Unmatched braces: {open_braces} opening, {close_braces} closing")
            
            open_parens = sling_model.count('(')
            close_parens = sling_model.count(')')
            if open_parens != close_parens:
                issues.append(f"Unmatched parentheses: {open_parens} opening, {close_parens} closing")
            
            # Check for proper getter methods
            value_map_fields = re.findall(r'@ValueMapValue[^;]*private\s+\w+\s+(\w+);', sling_model)
            for field in value_map_fields:
                getter_name = f"get{field.capitalize()}"
                if getter_name not in sling_model:
                    issues.append(f"Missing getter method '{getter_name}()' for field '{field}'")
        
        # Check HTL for proper syntax
        htl_content = files.get('htl', '')
        if htl_content:
            # Check for unmatched HTML tags
            open_tags = re.findall(r'<(\w+)[^>]*(?<!/)>', htl_content)
            close_tags = re.findall(r'</(\w+)>', htl_content)
            
            for tag in open_tags:
                if tag not in close_tags:
                    issues.append(f"Unmatched HTML tag: <{tag}> has no closing tag")
            
            # Check for proper data-sly-use syntax
            sly_use_matches = re.findall(r'data-sly-use\.\w+="([^"]*)"', htl_content)
            for match in sly_use_matches:
                if not re.match(r'^[a-zA-Z][a-zA-Z0-9.]*$', match):
                    issues.append(f"Invalid data-sly-use class name: {match}")
        
        return issues
    
    def _check_security_vulnerabilities(self, files: Dict[str, Any]) -> List[str]:
        """Check for security vulnerabilities"""
        issues = []
        
        # Check all string content for vulnerabilities
        all_content = ''
        for file_name, content in files.items():
            if isinstance(content, str):
                all_content += f"\n--- {file_name} ---\n{content}\n"
        
        # XSS vulnerabilities
        xss_patterns = [
            (r'innerHTML\s*=', "Potential XSS: Use textContent instead of innerHTML"),
            (r'document\.write\s*\(', "Potential XSS: Avoid document.write()"),
            (r'eval\s*\(', "Security risk: Avoid eval() function"),
            (r'Function\s*\(', "Security risk: Avoid Function() constructor"),
            (r'setTimeout\s*\([^,)]*["\'][^"\']*["\']', "Potential XSS: Avoid string-based setTimeout"),
            (r'setInterval\s*\([^,)]*["\'][^"\']*["\']', "Potential XSS: Avoid string-based setInterval")
        ]
        
        for pattern, message in xss_patterns:
            if re.search(pattern, all_content, re.IGNORECASE):
                issues.append(message)
        
        # SQL Injection checks (for any database queries)
        sql_patterns = [
            (r'SELECT\s+.*\+.*FROM', "Potential SQL injection: Use parameterized queries"),
            (r'INSERT\s+.*\+.*VALUES', "Potential SQL injection: Use parameterized queries"),
            (r'UPDATE\s+.*SET.*\+', "Potential SQL injection: Use parameterized queries"),
            (r'DELETE\s+.*WHERE.*\+', "Potential SQL injection: Use parameterized queries")
        ]
        
        for pattern, message in sql_patterns:
            if re.search(pattern, all_content, re.IGNORECASE):
                issues.append(message)
        
        # Check for hardcoded secrets
        secret_patterns = [
            (r'password\s*=\s*["\'][^"\']+["\']', "Hardcoded password detected"),
            (r'secret\s*=\s*["\'][^"\']+["\']', "Hardcoded secret detected"),
            (r'api[_-]?key\s*=\s*["\'][^"\']+["\']', "Hardcoded API key detected"),
            (r'token\s*=\s*["\'][^"\']+["\']', "Hardcoded token detected")
        ]
        
        for pattern, message in secret_patterns:
            if re.search(pattern, all_content, re.IGNORECASE):
                issues.append(message)
        
        # Check Sling Model specific security issues
        sling_model = files.get('slingModel', '')
        if sling_model:
            # Check for proper input validation
            if '@ValueMapValue' in sling_model and 'StringUtils' not in sling_model:
                issues.append("Consider adding input validation using StringUtils or similar")
            
            # Check for resource leaks
            if 'ResourceResolver' in sling_model and 'close()' not in sling_model:
                issues.append("Potential resource leak: ResourceResolver should be properly closed")
            
            # Check for proper null handling
            value_map_fields = re.findall(r'@ValueMapValue[^;]*private\s+\w+\s+(\w+);', sling_model)
            for field in value_map_fields:
                getter_pattern = f"get{field.capitalize()}\\(\\)"
                if re.search(getter_pattern, sling_model):
                    getter_content = re.search(f"get{field.capitalize()}\\(\\)\\s*{{([^}}]+)}}", sling_model)
                    if getter_content and 'null' not in getter_content.group(1).lower():
                        issues.append(f"Getter for '{field}' should include null safety check")
        
        # Check HTL for XSS prevention
        htl_content = files.get('htl', '')
        if htl_content:
            # Check for unescaped output
            unescaped_patterns = re.findall(r'\$\{[^}]*@\s*context\s*=\s*["\']unsafe["\'][^}]*\}', htl_content)
            if unescaped_patterns:
                issues.append("Unsafe context detected in HTL - potential XSS vulnerability")
            
            # Check for direct JavaScript injection
            if re.search(r'<script[^>]*>\s*\$\{', htl_content):
                issues.append("Direct variable injection in script tag - potential XSS")
        
        return issues