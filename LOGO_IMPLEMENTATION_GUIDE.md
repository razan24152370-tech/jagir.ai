# Logo Implementation Guide

## Overview
Your Pro Recruiter AI project now uses SVG logos across the entire application. The logos are intelligently displayed based on background color - blue logo for light backgrounds and white logo for dark backgrounds.

## Logo Files Location
```
accounts/static/images/
├── Blue_Logo.svg      # For light backgrounds (Navbar, main content areas)
└── White_Logo.svg     # For dark backgrounds (Footer, Sidebar)
```

## Logo Usage Across Application

### 1. **Navbar** (Light Background)
- **File Used**: `Blue_Logo.svg`
- **Location**: [templates/base.html](templates/base.html#L151)
- **Display**: Logo + "Pro Recruiter AI" text (hidden on mobile, visible on tablet+)
- **Class**: `.navbar-brand`
- **Size**: 40px height (auto width)

```html
<a class="navbar-brand" href="{% url 'project_home' %}">
    <img src="{% static 'images/Blue_Logo.svg' %}" alt="Pro Recruiter AI Logo" class="logo-img">
    <span>Pro Recruiter AI</span>
</a>
```

### 2. **Footer** (Dark Background)
- **File Used**: `White_Logo.svg`
- **Location**: [templates/base.html](templates/base.html#L240)
- **Display**: Logo + "Pro Recruiter AI" text
- **Class**: `.footer-brand`
- **Size**: 40px height (auto width)
- **Special**: Includes brightness filter for enhanced visibility

```html
<div class="footer-brand">
    <img src="{% static 'images/White_Logo.svg' %}" alt="Pro Recruiter AI Logo" class="logo-img">
    <span>Pro Recruiter AI</span>
</div>
```

### 3. **Dashboard Sidebar** (Dark Background)
- **File Used**: `White_Logo.svg`
- **Location**: [templates/dashboard_base.html](templates/dashboard_base.html#L357)
- **Display**: Logo + "Recruiter" text (hidden on mobile)
- **Class**: `.sidebar-logo`
- **Size**: 40px height (auto width)
- **Special**: Hover effect with scale and brightness transitions

```html
<a href="{% url 'project_home' %}" class="sidebar-logo">
    <img src="{% static 'images/White_Logo.svg' %}" alt="Pro Recruiter AI Logo" class="logo-img">
    <span>Recruiter</span>
</a>
```

## Styling System

### CSS Files Involved

#### 1. **logo_styles.css** (NEW - Comprehensive Logo Styling)
- **Location**: [accounts/static/logo_styles.css](accounts/static/logo_styles.css)
- **Purpose**: Dedicated logo styling for all logo instances
- **Includes**:
  - Base logo styling (sizing, animations)
  - Navbar logo styles
  - Footer logo styles
  - Sidebar logo styles
  - Responsive design (mobile, tablet, desktop)
  - Dark mode support
  - Accessibility features

#### 2. **admin_theme.css** (UPDATED)
- **Location**: [accounts/static/admin_theme.css](accounts/static/admin_theme.css)
- **Updates**: Added additional logo styling sections at the end
- **Fallback styling** for logo display across admin pages

#### 3. **base.html Inline Styles** (UPDATED)
- **Location**: [templates/base.html](templates/base.html#L30-L56)
- **Updates**: 
  - Modified `.navbar-brand` styling
  - Modified `.footer-brand` styling
  - Added logo-specific media queries

#### 4. **dashboard_base.html Inline Styles** (UPDATED)
- **Location**: [templates/dashboard_base.html](templates/dashboard_base.html#L58-L75)
- **Updates**: 
  - Modified `.sidebar-logo` styling
  - Added logo image sizing

## Features

### Responsive Design
| Device | Display | Logo Height |
|--------|---------|-------------|
| Mobile (<577px) | Logo only | 32px |
| Tablet (577-768px) | Logo only | 36px |
| Desktop (>768px) | Logo + Text | 40px |

### Interactive Effects
- **Hover Effect**: Logos scale to 105% on hover
- **Active State**: Logos scale to 98% on click
- **Smooth Transitions**: 0.3s ease transitions

### Theme Support
- **Light Background**: Blue logo with text
- **Dark Background**: White logo with brightness filter
- **Auto Detection**: CSS media query support for `prefers-color-scheme: dark`

### Accessibility
- **Alt Text**: All logos have descriptive alt text
- **Reduced Motion**: Respects `prefers-reduced-motion` setting
- **Print Friendly**: Logos display properly in print preview

## Customization Guide

### Changing Logo Size
Edit the `.logo-img` class in `logo_styles.css`:
```css
.logo-img {
    height: 40px;  /* Change this value */
    width: auto;
    max-width: 150px;
}
```

### Changing Logo Animation Speed
Edit the `transition` property in `logo_styles.css`:
```css
.logo-img {
    transition: all 0.3s ease;  /* Change 0.3s to desired duration */
}
```

### Changing Hover Effect
Edit the `.navbar-brand:hover .logo-img` rule:
```css
.navbar-brand:hover .logo-img {
    transform: scale(1.05);  /* Change scale value */
}
```

### Changing Footer Logo Brightness
Edit the `.footer-brand .logo-img` filter:
```css
.footer-brand .logo-img {
    filter: brightness(1.1);  /* Increase or decrease brightness */
}
```

## Template Integration

### Adding Logo to a New Template
1. Ensure the template has `{% load static %}` at the top
2. Link the logo CSS file in the `<head>`:
   ```html
   <link rel="stylesheet" href="{% static 'logo_styles.css' %}">
   ```
3. Add the appropriate logo element:
   ```html
   <!-- For light backgrounds (Navbar) -->
   <a class="navbar-brand" href="{% url 'project_home' %}">
       <img src="{% static 'images/Blue_Logo.svg' %}" alt="Pro Recruiter AI Logo" class="logo-img">
       <span>Pro Recruiter AI</span>
   </a>
   
   <!-- For dark backgrounds (Footer/Sidebar) -->
   <a class="sidebar-logo" href="{% url 'project_home' %}">
       <img src="{% static 'images/White_Logo.svg' %}" alt="Pro Recruiter AI Logo" class="logo-img">
       <span>Your Text</span>
   </a>
   ```

## Browser Compatibility
- ✅ Chrome/Edge (Latest)
- ✅ Firefox (Latest)
- ✅ Safari (Latest)
- ✅ Mobile Browsers (iOS Safari, Chrome Mobile)

## Performance Notes
- SVG logos are lightweight and scale perfectly at any size
- No additional HTTP requests beyond the static file serving
- Logos use CSS transitions (hardware-accelerated on modern browsers)
- Print-optimized versions included

## Testing Checklist
- [ ] Ensure logos display on all pages
- [ ] Test navbar logo on mobile, tablet, and desktop
- [ ] Test footer logo displays correctly with white background
- [ ] Test sidebar logo in dashboard
- [ ] Verify hover effects work smoothly
- [ ] Test responsive breakpoints (576px, 768px)
- [ ] Test dark mode detection (if applicable)
- [ ] Print page and verify logo visibility

## File Changes Summary
| File | Change Type | Description |
|------|------------|-------------|
| [templates/base.html](templates/base.html) | Modified | Updated navbar and footer to use SVG logos |
| [templates/dashboard_base.html](templates/dashboard_base.html) | Modified | Updated sidebar to use SVG logo |
| [accounts/static/logo_styles.css](accounts/static/logo_styles.css) | Created | Comprehensive logo styling system |
| [accounts/static/admin_theme.css](accounts/static/admin_theme.css) | Modified | Added logo styling sections |

## Need to Replace Logos?
To use different logo files:
1. Replace the SVG files in `accounts/static/images/`
2. Ensure file names match exactly (Blue_Logo.svg, White_Logo.svg)
3. Verify SVG is optimized and properly formatted
4. Clear browser cache to see changes

## Support
For logo-related issues, check:
1. SVG files exist in `accounts/static/images/`
2. CSS file is linked in template head
3. `{% load static %}` tag is present at top of template
4. Static files have been collected (run `python manage.py collectstatic` for production)
