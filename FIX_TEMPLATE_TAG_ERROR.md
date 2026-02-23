# Fix: TemplateSyntaxError - 'currency_filters' is not a registered tag library

## Problem
Django error: `'currency_filters' is not a registered tag library`

## Solution

### Step 1: Restart Django Development Server

**If running Django development server:**
1. Stop the server (Ctrl+C in terminal)
2. Wait 2-3 seconds
3. Restart with: `python manage.py runserver`

**If running in IDE (VSCode, PyCharm, etc.):**
1. Stop the debug session
2. Kill any Python processes related to Django
3. Restart the debug session

**If running with Gunicorn/uWSGI:**
1. Restart the application server
2. `systemctl restart gunicorn` (or your service name)
3. Or manually stop/start the process

### Step 2: Clear Python Cache (Important!)

Run one of these commands:

```bash
# Option 1: Delete __pycache__ directories
find . -type d -name __pycache__ -exec rm -r {} +

# Option 2: Clear specific cache
python -c "import py_compile; py_compile.compile('core/templatetags/currency_filters.py')"

# Option 3: Full clean (development only)
python manage.py collectstatic --noinput
python manage.py makemigrations
python manage.py migrate
```

### Step 3: Verify the Fix

Navigate to any page that uses currency formatting:
- Customer Dashboard: `/customer/dashboard/`
- Order List: `/customer/history/`
- Any page with `{% load currency_filters %}`

If you see the amounts with commas (₱1,234.56), it's working!

## Why This Happens

Django caches template tag library locations. When you create a new templatetags module:
1. Django doesn't know about it yet
2. Server must be restarted to reload the app registry
3. Python cache may have old module information
4. Browser cache might have old page versions

## Verification Steps

### 1. Check File Structure
```
core/
├── templatetags/          ← Must exist
│   ├── __init__.py       ← Must exist (can be empty)
│   └── currency_filters.py ← Must exist
├── models.py
├── views.py
└── ...
```

### 2. Check Settings
Open `PrycegasStation/settings.py` and verify:
```python
INSTALLED_APPS = [
    ...
    'core',  # Must be here
]
```

### 3. Test Import
Run in Python shell:
```python
python manage.py shell
>>> from django.template.loader import get_template
>>> from core.templatetags import currency_filters
>>> print(currency_filters.currency_format(1234.56))
# Should print: 1,234.56
```

### 4. Check Template
Look for line in template:
```django
{% load currency_filters %}  ← Must be present at top
```

## If Problem Persists

### Check 1: Python Path
```bash
python -c "import core.templatetags.currency_filters; print('OK')"
# Should print: OK
```

### Check 2: File Permissions
Ensure file is readable:
```bash
ls -la core/templatetags/currency_filters.py
# Should show readable permissions
```

### Check 3: Django Shell Test
```bash
python manage.py shell
>>> from core.templatetags.currency_filters import currency_format
>>> currency_format(1000)
'1,000.00'
```

### Check 4: Reload Module
Force reload in development:
```bash
# Edit any file in core/templatetags/ and save
# Django should auto-reload
# Or manually:
python manage.py shell
>>> import importlib
>>> import core.templatetags.currency_filters
>>> importlib.reload(core.templatetags.currency_filters)
```

## Common Mistakes

❌ **Wrong:** templatetags folder not created  
✅ **Right:** `core/templatetags/` folder exists

❌ **Wrong:** No `__init__.py` in templatetags  
✅ **Right:** `core/templatetags/__init__.py` exists (can be empty)

❌ **Wrong:** Not restarting server  
✅ **Right:** Kill server and restart it

❌ **Wrong:** Template doesn't have load tag  
✅ **Right:** `{% load currency_filters %}` at top

❌ **Wrong:** Typo in template tag name  
✅ **Right:** `currency_filters` (not `currency_filter`)

## Quick Checklist

- [ ] Server restarted
- [ ] Cache cleared
- [ ] `core/templatetags/` folder exists
- [ ] `core/templatetags/__init__.py` exists
- [ ] `core/templatetags/currency_filters.py` exists
- [ ] `core` in INSTALLED_APPS
- [ ] Template has `{% load currency_filters %}`
- [ ] Filter name in template is `currency_format` (not `currency_formats`)
- [ ] Tested in Python shell
- [ ] Page loads without error

## Still Broken?

If the problem persists:
1. Check browser console for errors (F12)
2. Check Django server logs for full error trace
3. Verify exact error line number in template
4. Check that all 3 files exist: `__init__.py`, `currency_filters.py`
5. Restart VS Code or IDE completely
6. Delete `.venv` and recreate if very stuck (nuclear option)

## Success

When working, you'll see:
```
Page loads: ✅
Amounts show commas: ✅
No template errors: ✅
Grand total displays: ✅
```

---

**TL;DR: Restart Django server with `python manage.py runserver`**
