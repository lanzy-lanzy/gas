# How to Add Notification Bell to Your Template

## Quick Integration

### Step 1: Locate Your Base Template
Find your main base template (usually `templates/base.html`)

### Step 2: Add the Bell Component
Add this line to your navbar/header where you want the notification bell to appear:

```html
{% if user.is_authenticated %}
    {% include 'components/notification_bell.html' %}
{% endif %}
```

### Step 3: Example Placements

#### Example 1: Bootstrap Navbar
```html
<nav class="navbar navbar-expand-lg navbar-light bg-light">
    <div class="container-fluid">
        <a class="navbar-brand" href="/">Prycegas</a>
        
        <div class="navbar-collapse ms-auto">
            <ul class="navbar-nav ms-auto">
                <li class="nav-item">
                    {% if user.is_authenticated %}
                        {% include 'components/notification_bell.html' %}
                    {% endif %}
                </li>
                <li class="nav-item">
                    <a class="nav-link" href="{% url 'core:profile' %}">
                        Profile
                    </a>
                </li>
                <li class="nav-item">
                    <a class="nav-link" href="{% url 'core:logout' %}">
                        Logout
                    </a>
                </li>
            </ul>
        </div>
    </div>
</nav>
```

#### Example 2: Tailwind Navbar
```html
<nav class="bg-white shadow-md">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center h-16">
            <h1 class="text-2xl font-bold">Prycegas</h1>
            
            <div class="flex items-center gap-6">
                {% if user.is_authenticated %}
                    {% include 'components/notification_bell.html' %}
                    <a href="{% url 'core:profile' %}">Profile</a>
                    <a href="{% url 'core:logout' %}">Logout</a>
                {% endif %}
            </div>
        </div>
    </div>
</nav>
```

#### Example 3: Custom Header
```html
<header class="site-header">
    <div class="header-content">
        <div class="logo">
            <a href="/">Prycegas</a>
        </div>
        
        <div class="header-nav">
            {% if user.is_authenticated %}
                <div class="nav-item">
                    {% include 'components/notification_bell.html' %}
                </div>
                <div class="nav-item">
                    <a href="{% url 'core:profile' %}">Profile</a>
                </div>
                <div class="nav-item">
                    <a href="{% url 'core:logout' %}">Logout</a>
                </div>
            {% endif %}
        </div>
    </div>
</header>
```

## Styling Integration

### If Using Bootstrap
The notification bell includes its own CSS, but you can override with Bootstrap classes:

```html
<style>
    .notification-bell {
        width: auto;
        height: auto;
        padding: 0.5rem;
    }
    
    .notification-dropdown {
        min-width: 350px;
    }
</style>
```

### If Using Tailwind
Add custom styles for Tailwind compatibility:

```html
<style>
    .notification-bell {
        @apply relative inline-flex items-center justify-center w-10 h-10 text-gray-700 cursor-pointer hover:text-blue-600 transition-colors;
    }
    
    .notification-badge {
        @apply absolute top-0 right-0 flex items-center justify-center w-5 h-5 -mx-1 -my-1 bg-red-500 text-white text-xs font-bold rounded-full border-2 border-white;
    }
</style>
```

### Custom Styling
Edit the CSS in `templates/components/notification_bell.html` directly to match your theme.

## Mobile Responsiveness

The notification bell is fully responsive. On mobile:
- Bell icon displays normally
- Badge shows count
- Dropdown appears on tap with adjusted width
- Touch-friendly button sizes

For better mobile experience, you can customize:

```css
@media (max-width: 768px) {
    .notification-dropdown {
        width: 300px;
        right: -50px;
    }
    
    .notification-item {
        padding: 8px 12px;
    }
}
```

## JavaScript Dependencies

The component includes its own JavaScript. If you need jQuery or other dependencies:

```html
<!-- Optional: Use with jQuery -->
<script>
document.addEventListener('DOMContentLoaded', function() {
    // Component initializes automatically
});
</script>
```

## Customization Examples

### Hide Badge When No Unread
Edit `notification_bell.html`:
```html
{% if unread_notification_count > 0 %}
    <span class="notification-badge">{{ unread_notification_count }}</span>
{% endif %}
```

### Change Dropdown Position
```css
.notification-dropdown {
    /* Change from right: 0 to left for left alignment */
    left: 0;
    right: auto;
}
```

### Custom Icons
Replace SVG icons with Font Awesome or custom icons:

```html
<!-- Using Font Awesome -->
<i class="fas fa-bell"></i>

<!-- Or custom image -->
<img src="{% static 'images/bell.svg' %}" alt="Notifications">
```

## Troubleshooting

### Bell Not Showing
1. Check `user.is_authenticated` is True
2. Verify path to component: `templates/components/notification_bell.html`
3. Check template loads without errors
4. Browser console for JavaScript errors

### Dropdown Not Opening
1. Check CSS loads correctly
2. Verify hover states work
3. Check z-index not being overridden
4. Test on different browsers

### Wrong Position
1. Check parent element `position: relative`
2. Verify dropdown CSS `position: absolute`
3. Adjust top/right values in CSS
4. Check for overflow: hidden on parent

### Styling Conflict
1. Check CSS specificity
2. Use `!important` if needed (temporary)
3. Move CSS to separate stylesheet
4. Check for duplicate CSS rules

## Full Template Example

Here's a complete minimal example:

```html
<!DOCTYPE html>
<html>
<head>
    <title>{% block title %}Prycegas{% endblock %}</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: Arial, sans-serif; background: #f5f5f5; }
        
        .navbar {
            background: white;
            padding: 1rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .navbar-brand { font-size: 1.5rem; font-weight: bold; }
        
        .navbar-nav {
            display: flex;
            gap: 2rem;
            align-items: center;
            list-style: none;
        }
        
        .navbar-nav a { text-decoration: none; color: #333; }
        .navbar-nav a:hover { color: #0066cc; }
    </style>
</head>
<body>
    <nav class="navbar">
        <div class="navbar-brand">Prycegas</div>
        
        <ul class="navbar-nav">
            {% if user.is_authenticated %}
                <li>
                    {% include 'components/notification_bell.html' %}
                </li>
                <li><a href="{% url 'core:customer_dashboard' %}">Dashboard</a></li>
                <li><a href="{% url 'core:profile' %}">{{ user.username }}</a></li>
                <li><a href="{% url 'core:logout' %}">Logout</a></li>
            {% else %}
                <li><a href="{% url 'core:login' %}">Login</a></li>
                <li><a href="{% url 'core:register' %}">Register</a></li>
            {% endif %}
        </ul>
    </nav>
    
    <main class="container">
        {% block content %}{% endblock %}
    </main>
</body>
</html>
```

## Performance Notes

The notification bell component is optimized:
- Minimal JavaScript (only 50 lines)
- CSS included inline in component
- No external dependencies
- Fast hover/dropdown transitions
- Lazy loads notification data

## Accessibility Features

The component includes:
- Semantic HTML structure
- ARIA labels for screen readers
- Keyboard navigation support
- Color contrast compliance
- Focus indicators

## Browser Compatibility

- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+
- ✅ Mobile browsers (iOS Safari, Chrome Mobile)

## Context Variables Available

In your base template, you can use:

```html
<!-- Direct access to notifications -->
{{ unread_notifications }}           <!-- Latest 5 unread -->
{{ unread_notification_count }}      <!-- Count of unread -->

<!-- Check if has notifications -->
{% if unread_notification_count > 0 %}
    User has {{ unread_notification_count }} unread notifications
{% endif %}

<!-- Loop through notifications -->
{% for notif in unread_notifications %}
    <p>{{ notif.title }}: {{ notif.message }}</p>
{% endfor %}
```

## Advanced Customization

### Custom Notification Card Template
Create `templates/components/notification_item.html`:

```html
<div class="notification-item" data-notification-id="{{ notification.id }}">
    <h5>{{ notification.title }}</h5>
    <p>{{ notification.message }}</p>
    {% if notification.reason %}
        <small>Reason: {{ notification.reason }}</small>
    {% endif %}
</div>
```

Then include it in the bell:
```html
{% for notification in unread_notifications %}
    {% include 'components/notification_item.html' %}
{% endfor %}
```

### AJAX Polling (Optional)
Add auto-refresh of notification count:

```html
<script>
function updateNotificationCount() {
    fetch('/api/notifications/unread-count/')
        .then(r => r.json())
        .then(data => {
            const badge = document.querySelector('.notification-badge');
            if (data.unread_count > 0) {
                badge.textContent = data.unread_count;
            } else if (badge) {
                badge.remove();
            }
        });
}

// Update every 30 seconds
setInterval(updateNotificationCount, 30000);
</script>
```

---

## Summary

1. ✅ Add `{% include 'components/notification_bell.html' %}` to your navbar
2. ✅ Wrap in `{% if user.is_authenticated %}`
3. ✅ Customize CSS if needed
4. ✅ Test on mobile and desktop
5. ✅ Enjoy! 🎉

**File Location:** `templates/components/notification_bell.html`  
**Integration Time:** < 5 minutes  
**Difficulty:** Easy  
**No JavaScript Required:** (Component handles its own)

