# AEM Component Prompts for DXP Generator

## 1. Hero Banner Component

**Prompt:**
```
Create a responsive and accessible AEM Hero Banner component based on the provided image. The component should include:

**Functional Requirements:**
- Full-width hero section with background image/video support
- Overlay text with headline, subheadline, and CTA buttons
- Responsive breakpoints for mobile, tablet, and desktop
- Support for multiple content alignment options (left, center, right)
- Optional dark/light overlay for text readability

**Technical Requirements:**
- Generate HTL template with proper semantic HTML5 structure
- Create Sling Model with @Model annotation and proper OSGi practices
- Implement author dialog with image upload, text fields, and alignment options
- Include context.xml with component group and allowed parents
- Responsive CSS with mobile-first approach and CSS Grid/Flexbox
- JavaScript for lazy loading and scroll animations (if needed)
- JUnit tests for Sling Model validation

**Accessibility Requirements:**
- ARIA labels and roles for screen readers
- Proper heading hierarchy (h1-h6)
- Alt text for background images
- Keyboard navigation support
- Color contrast compliance (WCAG 2.1 AA)
- Focus indicators for interactive elements

**Additional Features:**
- Support for AEM Dynamic Media integration
- Content fragment integration capability
- Experience Fragment support
- Multi-language support with i18n
```

## 2. Card Grid Component

**Prompt:**
```
Create a responsive and accessible AEM Card Grid component based on the provided image. The component should include:

**Functional Requirements:**
- Flexible grid layout supporting 1-4 columns
- Individual cards with image, title, description, and CTA
- Hover effects and animations
- Filter and sort functionality (optional)
- Load more/pagination support

**Technical Requirements:**
- Generate HTL template with proper card structure and grid system
- Create Sling Model with card data handling and pagination logic
- Implement author dialog with multifield for card configuration
- Include context.xml with component policies
- CSS Grid/Flexbox responsive layout with smooth transitions
- JavaScript for interactions, filtering, and lazy loading
- JUnit tests for model logic and data validation

**Accessibility Requirements:**
- Semantic HTML with proper landmark roles
- Screen reader friendly card navigation
- Keyboard accessibility for all interactive elements
- ARIA-expanded states for expandable content
- Image alt text requirements
- Focus management for dynamic content

**Additional Features:**
- Integration with AEM Content Fragments
- Support for external data sources via OSGi services
- Configurable animation effects
- SEO-friendly markup with structured data
```

## 3. Navigation Menu Component

**Prompt:**
```
Create a responsive and accessible AEM Navigation Menu component based on the provided image. The component should include:

**Functional Requirements:**
- Multi-level dropdown navigation (up to 3 levels)
- Mobile hamburger menu with slide-out panel
- Mega menu support for complex navigation structures
- Active state indication for current page
- Breadcrumb integration capability

**Technical Requirements:**
- Generate HTL template with nested navigation structure
- Create Sling Model for page hierarchy and navigation logic
- Implement author dialog with navigation root and depth configuration
- Include context.xml with appropriate component group
- Mobile-first responsive CSS with smooth animations
- JavaScript for mobile menu toggle and dropdown interactions
- JUnit tests for navigation building logic

**Accessibility Requirements:**
- ARIA navigation landmarks and menu roles
- Keyboard navigation with arrow keys and Enter/Escape
- Screen reader announcements for menu state changes
- Skip links for keyboard users
- Proper focus management in dropdown menus
- Mobile menu accessible button states

**Additional Features:**
- Integration with AEM site structure
- Support for external links and custom URLs
- Configurable menu styling options
- Search integration within navigation
```

## 4. Content Carousel Component

**Prompt:**
```
Create a responsive and accessible AEM Content Carousel component based on the provided image. The component should include:

**Functional Requirements:**
- Multi-slide carousel with previous/next navigation
- Dot pagination indicators
- Auto-play functionality with pause on hover
- Touch/swipe support for mobile devices
- Variable slide content (images, text, mixed media)

**Technical Requirements:**
- Generate HTL template with carousel structure and slide containers
- Create Sling Model for slide data management and configuration
- Implement author dialog with multifield for slide configuration
- Include context.xml with component policies
- CSS for smooth transitions and responsive behavior
- JavaScript using modern carousel libraries or vanilla JS
- JUnit tests for slide data handling and validation

**Accessibility Requirements:**
- ARIA live regions for slide changes
- Keyboard navigation with arrow keys
- Screen reader friendly slide announcements
- Pause/play controls for auto-advancing content
- Reduced motion support for users with vestibular disorders
- Proper heading structure within slides

**Additional Features:**
- Infinite loop capability
- Configurable transition effects
- Integration with AEM Assets and Dynamic Media
- Analytics tracking for slide interactions
```

## 5. Form Container Component

**Prompt:**
```
Create a responsive and accessible AEM Form Container component based on the provided image. The component should include:

**Functional Requirements:**
- Multi-step form support with progress indicators
- Various field types (text, email, phone, dropdown, radio, checkbox)
- Client-side and server-side validation
- File upload capability with drag-and-drop
- Form submission handling with success/error states

**Technical Requirements:**
- Generate HTL template with semantic form structure
- Create Sling Model for form processing and validation
- Implement author dialog for form configuration and field management
- Include context.xml with form-specific policies
- CSS for form styling and responsive layout
- JavaScript for validation, interactions, and AJAX submission
- JUnit tests for form validation and submission logic

**Accessibility Requirements:**
- Proper form labels and field associations
- Error message announcements
- Required field indicators
- Fieldset and legend for grouped fields
- Keyboard navigation between form elements
- Screen reader compatible validation feedback

**Additional Features:**
- Integration with AEM Forms or third-party form services
- CAPTCHA/reCAPTCHA support
- Form analytics and conversion tracking
- Multi-language form support
```

## 6. Testimonial Slider Component

**Prompt:**
```
Create a responsive and accessible AEM Testimonial Slider component based on the provided image. The component should include:

**Functional Requirements:**
- Customer testimonials with photos, quotes, and attribution
- Sliding/fading transitions between testimonials
- Star rating display
- Company logo integration
- Social media link integration

**Technical Requirements:**
- Generate HTL template with testimonial card structure
- Create Sling Model for testimonial data management
- Implement author dialog with multifield for testimonial entries
- Include context.xml with component configuration
- CSS for elegant testimonial presentation and transitions
- JavaScript for slider functionality and smooth animations
- JUnit tests for testimonial data validation

**Accessibility Requirements:**
- Proper quote markup with blockquote elements
- Image alt text for customer photos
- Screen reader friendly slider controls
- Keyboard navigation support
- Pause control for auto-advancing content
- Semantic markup for ratings and attribution

**Additional Features:**
- Integration with review platforms (Google, Yelp, etc.)
- Schema.org markup for rich snippets
- Social sharing capabilities
- Testimonial filtering by category or rating
```

## 7. Accordion/FAQ Component

**Prompt:**
```
Create a responsive and accessible AEM Accordion/FAQ component based on the provided image. The component should include:

**Functional Requirements:**
- Expandable/collapsible content sections
- Support for rich text content in answers
- Search functionality within FAQ items
- Single or multiple panel expansion modes
- Icon indicators for expand/collapse states

**Technical Requirements:**
- Generate HTL template with proper accordion structure
- Create Sling Model for FAQ data handling and search logic
- Implement author dialog with multifield for FAQ entries
- Include context.xml with component policies
- CSS for smooth expand/collapse animations
- JavaScript for accordion interactions and search functionality
- JUnit tests for FAQ data management and search logic

**Accessibility Requirements:**
- ARIA expanded/collapsed states
- Keyboard navigation with Enter and Space keys
- Screen reader friendly expand/collapse announcements
- Proper heading hierarchy for FAQ questions
- Focus management during panel transitions
- Skip links for long FAQ lists

**Additional Features:**
- Deep linking to specific FAQ items
- FAQ analytics and popular question tracking
- Integration with site search functionality
- Export FAQ data functionality
```

## 8. Video Player Component

**Prompt:**
```
Create a responsive and accessible AEM Video Player component based on the provided image. The component should include:

**Functional Requirements:**
- HTML5 video player with custom controls
- Multiple video format support (MP4, WebM, etc.)
- Poster image and thumbnail support
- Playlist functionality for multiple videos
- Fullscreen and picture-in-picture modes

**Technical Requirements:**
- Generate HTL template with video element and custom controls
- Create Sling Model for video metadata and configuration
- Implement author dialog for video upload and settings
- Include context.xml with media-specific policies
- CSS for custom player styling and responsive behavior
- JavaScript for player controls and functionality
- JUnit tests for video configuration and playback logic

**Accessibility Requirements:**
- Closed captions and subtitle support
- Keyboard controls for play/pause/seek
- Screen reader announcements for player state
- High contrast mode support for controls
- Audio description track support
- Transcript availability

**Additional Features:**
- Integration with AEM Dynamic Media
- Video analytics and engagement tracking
- Adaptive bitrate streaming support
- Social sharing with video timestamps
```

## 9. Image Gallery Component

**Prompt:**
```
Create a responsive and accessible AEM Image Gallery component based on the provided image. The component should include:

**Functional Requirements:**
- Grid-based image layout with multiple view options
- Lightbox functionality for enlarged image viewing
- Image filtering and sorting capabilities
- Lazy loading for performance optimization
- Thumbnail navigation in lightbox mode

**Technical Requirements:**
- Generate HTL template with responsive image grid
- Create Sling Model for image data and metadata handling
- Implement author dialog for gallery configuration and image management
- Include context.xml with image-specific policies
- CSS for responsive grid layouts and lightbox styling
- JavaScript for lightbox functionality and image interactions
- JUnit tests for image data handling and gallery logic

**Accessibility Requirements:**
- Alt text for all images
- Keyboard navigation in lightbox mode
- Screen reader compatible image descriptions
- Focus management during lightbox transitions
- ARIA labels for gallery controls
- Reduced motion support for animations

**Additional Features:**
- Integration with AEM Assets and Dynamic Media
- EXIF data display for photographers
- Social sharing for individual images
- Batch image upload functionality
```

## 10. Pricing Table Component

**Prompt:**
```
Create a responsive and accessible AEM Pricing Table component based on the provided image. The component should include:

**Functional Requirements:**
- Multiple pricing tiers with feature comparisons
- Highlighted recommended/popular plans
- Toggle between monthly/yearly pricing
- Feature tooltips and detailed descriptions
- Call-to-action buttons for each tier

**Technical Requirements:**
- Generate HTL template with table structure and responsive design
- Create Sling Model for pricing data and tier management
- Implement author dialog for pricing configuration and feature management
- Include context.xml with commerce-related policies
- CSS for responsive table layout and visual emphasis
- JavaScript for pricing toggle and interactive features
- JUnit tests for pricing calculations and data validation

**Accessibility Requirements:**
- Proper table headers and data cell associations
- Screen reader friendly pricing information
- Keyboard navigation for interactive elements
- High contrast support for pricing emphasis
- ARIA labels for pricing toggles and CTAs
- Clear focus indicators for all interactive elements

**Additional Features:**
- Currency localization support
- Integration with e-commerce platforms
- A/B testing capabilities for pricing strategies
- Analytics tracking for conversion optimization
```

## Common Technical Specifications for All Components

### File Structure Template:
```
/apps/[project]/components/[component-name]/
├── .content.xml
├── _cq_dialog.xml
├── [component-name].html (HTL)
├── [ComponentName]Model.java (Sling Model)
├── clientlibs/
│   ├── css/
│   │   └── [component-name].css
│   └── js/
│       └── [component-name].js
└── tests/
    └── [ComponentName]ModelTest.java
```

### Standard Dialog Properties:
- Component title and description
- Style system integration
- Responsive behavior settings
- Accessibility options
- Analytics tracking configuration

### CSS Standards:
- Mobile-first responsive design
- BEM methodology for class naming
- CSS custom properties for theming
- Support for RTL languages
- Performance optimized (critical CSS inline)

### JavaScript Standards:
- ES6+ modern JavaScript
- Event delegation patterns
- Intersection Observer for lazy loading
- Vanilla JS preferred over libraries (unless specified)
- Error handling and graceful degradation

### Testing Requirements:
- Unit tests for Sling Models
- Integration tests for component functionality
- Accessibility testing with automated tools
- Cross-browser compatibility testing
- Performance testing and optimization