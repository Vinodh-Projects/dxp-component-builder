#!/usr/bin/env python3
"""
Test script to demonstrate the fixed class name generation
"""

import re

def create_class_name_from_component_name(component_name: str) -> str:
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

# Test cases to demonstrate the fix
test_cases = [
    "feature-grid",
    "accordion", 
    "two-column-layout",
    "hero-banner",
    "contact-form",
    "navigation-menu",
    "card-grid",
    "image-carousel"
]

print("🔧 **Class Name Generation Fix Demonstration**\n")
print("This shows how component names are now converted to proper Java class names:\n")

for component_name in test_cases:
    class_name = create_class_name_from_component_name(component_name)
    print(f"Component Name: '{component_name}' → Class Name: '{class_name}'")

print(f"\n✅ **Fix Summary:**")
print(f"- Java filename will be: [ClassName].java")  
print(f"- Class declaration will be: public class [ClassName] {{")
print(f"- For example: 'feature-grid' → 'FeatureGridModel.java' with class 'FeatureGridModel'")
print(f"- This ensures filename and class name are properly synchronized!")
