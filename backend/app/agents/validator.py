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

2. AEM Best Practices
   - Proper resource types
   - Correct annotations
   - Appropriate injection strategies
   - Proper null handling

3. Performance
   - Lazy loading implemented
   - Efficient selectors
   - Optimized client libraries

4. Accessibility
   - ARIA labels present
   - Semantic HTML
   - Keyboard navigation support
   - Screen reader compatibility

5. Security
   - XSS prevention
   - Input validation
   - Safe resource handling

OUTPUT FORMAT:
{
  "validationStatus": "PASS/FAIL",
  "score": 0-100,
  "issues": ["list of issues"],
  "suggestions": ["list of suggestions"],
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
            if not files.get(req_file) or not files.get(req_file).strip():
                missing_files.append(req_file)
                scores["completeness"] -= 25

        if missing_files:
            issues.append(f"Missing or empty required files: {', '.join(missing_files)}")

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
   - Is the component production-ready?

2. **AEM BEST PRACTICES** (0-100):
   - Proper use of Sling Models and annotations
   - Correct HTL templating practices
   - Appropriate dialog structure
   - Resource type naming conventions
   - Component categorization

3. **PERFORMANCE** (0-100):
   - Efficient resource handling
   - Lazy loading implementation
   - Client library optimization
   - Caching considerations

4. **ACCESSIBILITY** (0-100):
   - WCAG 2.1 compliance
   - ARIA attributes and labels
   - Semantic HTML structure
   - Keyboard navigation support
   - Screen reader compatibility

5. **SECURITY** (0-100):
   - XSS prevention measures
   - Input validation and sanitization
   - Safe resource handling
   - Authentication considerations

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