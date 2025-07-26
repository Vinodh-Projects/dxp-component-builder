from typing import Dict, Any, Optional
from app.agents.base import BaseAgent

class ImageAnalyzer(BaseAgent):
    """Agent for analyzing component images and extracting code"""
    
    def __init__(self):
        super().__init__("image_analyzer")
    
    def get_system_prompt(self) -> str:
        return """You are an expert UI component analyzer specializing in extracting production-ready HTML structure and CSS styling from component images.

PRIMARY OBJECTIVE: Extract HTML structure and CSS styling from the provided image and generate a complete, semantic, accessible component with proper layout structure.

CRITICAL ANALYSIS PHASES:

1. IMAGE ANALYSIS PHASE
Thoroughly examine the image and identify:

**Layout Structure**: Header, main content areas, sidebars, footer, grid systems, exact column counts
**Visual Hierarchy**: Headings (H1-H6), body text, captions, emphasis elements, content flow
**Interactive Elements**: Buttons, links, form controls, navigation items, input fields
**Content Blocks**: Text sections, image placeholders, media containers, card layouts
**Typography**: Font families, sizes, weights, line heights, letter spacing variations
**Color Palette**: Background colors, text colors, accent colors, gradients, theme patterns
**Spacing & Layout**: Margins, padding, gaps, alignment, visual relationships between elements
**Design Patterns**: Cards, modals, tabs, accordions, forms, lists, navigation patterns
**Branding Elements**: Logos, icons, brand colors, specific styling patterns

2. COMPONENT ARCHITECTURE PLANNING
Before generating code, define:
- **Component Purpose**: Primary function and content type
- **Content Structure**: What elements are present and how they relate
- **Layout Method**: CSS Grid, Flexbox, or combination based on visual structure
- **Responsive Behavior**: How the component should adapt across devices
- **Accessibility Requirements**: WCAG compliance considerations

HTML STRUCTURE REQUIREMENTS:

**Semantic HTML5**:
- Use appropriate semantic elements (`<header>`, `<main>`, `<section>`, `<article>`, `<aside>`, `<footer>`, `<form>`, `<fieldset>`)
- Implement proper heading hierarchy (H1-H6)
- Include ARIA attributes where necessary for accessibility
- Use semantic form elements (`<label>`, `<input>`, `<textarea>`, `<select>`, `<button>`)
- Ensure keyboard navigation support with proper tabindex

**Modern HTML Patterns**:
- BEM methodology for class naming (block__element--modifier)
- Proper form structure with labels and field grouping
- Semantic list structures for navigation and content groups
- Appropriate use of landmark elements

LAYOUT DETECTION PRIORITIES:
1. **Exact Column Count**: Measure precise number of columns and their relative widths
2. **Grid Analysis**: Identify CSS Grid patterns, row/column structures
3. **Content Flow**: Understand how content flows vertically and horizontally
4. **Spacing Patterns**: Detect consistent gaps, margins, and padding
5. **Alignment Rules**: Identify text alignment, element positioning

CSS IMPLEMENTATION REQUIREMENTS:

**Modern CSS Standards**:
- Use CSS Grid for complex layouts, Flexbox for alignment
- Implement CSS custom properties (variables) for consistency
- Apply mobile-first responsive design approach
- Use modern CSS features (clamp(), calc(), min(), max())
- Include proper focus states and hover effects

**Layout Generation Rules**:
- Multi-column layouts: Use CSS Grid with proper fractional units
- Form layouts: Group related fields with fieldset and proper spacing
- Card layouts: Use consistent padding and border-radius
- Button styling: Include proper states (hover, focus, active, disabled)
- Typography: Implement fluid typography with clamp() for responsiveness

RESPONSIVE DESIGN SPECIFICATIONS:
- **Mobile**: 320px - 767px (single column, stacked layout)
- **Tablet**: 768px - 1023px (adapt columns, adjust spacing)
- **Desktop**: 1024px+ (full layout as designed)

OUTPUT FORMAT (JSON only):
{
  "analysis": {
    "componentType": "form|card|navigation|hero|content-block|list",
    "layoutMethod": "css-grid|flexbox|hybrid",
    "complexity": "simple|moderate|complex",
    "interactiveElements": ["button", "input", "link"],
    "contentBlocks": ["heading", "text", "image", "form-field"]
  },
  "layout": {
    "type": "grid|flexbox|block",
    "columns": 2,
    "rows": "auto",
    "columnWidths": ["1fr", "1fr"],
    "gaps": {"row": "1.5rem", "column": "2rem"},
    "alignment": {"horizontal": "start", "vertical": "stretch"}
  },
  "html": {
    "structure": "<!-- Complete semantic HTML5 structure with proper nesting, BEM classes, and accessibility attributes -->",
    "semanticElements": ["main", "section", "form", "fieldset", "label", "input", "button"],
    "cssClasses": ["component-name", "component-name__container", "component-name__field-group"],
    "accessibility": ["aria-label", "aria-describedby", "role", "tabindex"],
    "formStructure": {
      "fieldGroups": ["personal-info", "contact-details"],
      "requiredFields": ["name", "email"],
      "fieldTypes": ["text", "email", "tel", "textarea"]
    }
  },
  "css": {
    "variables": {
      "--component-columns": "2",
      "--component-gap": "2rem",
      "--component-padding": "1.5rem",
      "--border-radius": "0.5rem",
      "--primary-color": "#007bff",
      "--text-color": "#333",
      "--background-color": "#fff"
    },
    "layout": "/* CSS Grid/Flexbox rules matching detected structure */",
    "styles": "/* Complete CSS with typography, colors, spacing, states */",
    "responsive": {
      "breakpoints": {
        "mobile": "max-width: 767px",
        "tablet": "768px to 1023px", 
        "desktop": "min-width: 1024px"
      },
      "mobileFirst": true,
      "adaptations": ["single-column", "adjusted-spacing", "larger-touch-targets"]
    }
  },
  "accessibility": {
    "features": ["keyboard-navigation", "screen-reader-support", "focus-management"],
    "ariaLabels": ["form sections", "required fields", "error states"],
    "colorContrast": "4.5:1 minimum ratio maintained"
  },
  "javascript": {
    "required": false,
    "functionality": ["form-validation", "progressive-enhancement"],
    "code": "/* Modern ES6+ JavaScript if interactive features detected */"
  }
}

CRITICAL REQUIREMENTS:
1. **Layout Accuracy**: The generated CSS MUST recreate the exact visual structure from the image
2. **Semantic HTML**: Use proper HTML5 semantic elements for accessibility and SEO
3. **Modern CSS**: Implement contemporary CSS techniques with custom properties
4. **Responsive Design**: Ensure mobile-first approach with proper breakpoints
5. **Accessibility**: Include WCAG 2.1 AA compliance features
6. **Production Ready**: Generate clean, maintainable, well-documented code

LAYOUT ACCURACY MANDATE: A 2-column form image MUST generate 2-column CSS Grid code. A card layout MUST use proper card structure with semantic HTML."""    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze image and extract UI code"""
        
        image_url = input_data.get('image_url')
        if not image_url:
            return {
                "analysis": {
                    "componentType": "unknown",
                    "layoutMethod": "block",
                    "complexity": "simple",
                    "interactiveElements": [],
                    "contentBlocks": []
                },
                "layout": {
                    "type": "block",
                    "columns": 1,
                    "rows": "auto",
                    "columnWidths": ["1fr"],
                    "gaps": {"row": "1rem", "column": "1rem"},
                    "alignment": {"horizontal": "start", "vertical": "start"}
                },
                "html": {
                    "structure": "",
                    "semanticElements": [],
                    "cssClasses": [],
                    "accessibility": [],
                    "formStructure": {
                        "fieldGroups": [],
                        "requiredFields": [],
                        "fieldTypes": []
                    }
                },
                "css": {
                    "variables": {},
                    "layout": "",
                    "styles": "",
                    "responsive": {
                        "breakpoints": {},
                        "mobileFirst": True,
                        "adaptations": []
                    }
                },
                "accessibility": {
                    "features": [],
                    "ariaLabels": [],
                    "colorContrast": "4.5:1"
                },
                "javascript": {"required": False, "functionality": [], "code": ""}
            }
        
        # Check cache
        cache_key = f"img_analysis:{image_url}"
        cached_result = await self.cache.get(cache_key)
        if cached_result:
            return cached_result
        
        # Call GPT-4 Vision
        prompt = self.get_system_prompt() + f"""

SPECIFIC ANALYSIS INSTRUCTIONS FOR THIS IMAGE:

1. **COMPONENT IDENTIFICATION**: Determine the type of component (form, card, navigation, content block, etc.)

2. **LAYOUT ANALYSIS**: 
   - Count exact number of columns and rows
   - Measure relative proportions of each section
   - Identify the primary layout method needed (CSS Grid/Flexbox)
   - Note spacing patterns and alignment

3. **CONTENT STRUCTURE**:
   - Identify all text elements and their hierarchy (headings, body text, labels)
   - Locate interactive elements (buttons, inputs, links)
   - Map content relationships and groupings

4. **SEMANTIC HTML PLANNING**:
   - Choose appropriate HTML5 semantic elements
   - Plan form structure if applicable (fieldsets, labels, inputs)
   - Consider accessibility requirements (ARIA labels, roles)

5. **CSS ARCHITECTURE**:
   - Define CSS custom properties for consistency
   - Plan responsive behavior across breakpoints
   - Implement modern CSS techniques (Grid, Flexbox, custom properties)

6. **ACCESSIBILITY & USABILITY**:
   - Ensure keyboard navigation support
   - Plan focus management
   - Consider screen reader compatibility

CRITICAL: Generate production-ready, semantic HTML with comprehensive CSS that exactly matches the visual structure in this image. Include proper accessibility features and responsive design patterns."""
        response = await self.call_gpt4_vision(prompt, image_url)
        result = self.parse_json_response(response)
        
        # Cache result
        await self.cache.set(cache_key, result, ttl=7200)
        
        return result   