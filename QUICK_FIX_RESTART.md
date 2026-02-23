# Quick Fix - Restart Django Server

## Problem
Error: `'currency_filters' is not a registered tag library`

## Quick Solution (30 seconds)

### ✅ RESTART THE DJANGO SERVER

**In your terminal/command prompt where Django is running:**

1. **Stop the server** (press Ctrl+C)
2. **Wait 2 seconds**
3. **Restart it:**
   ```bash
   python manage.py runserver
   ```

**That's it!** Go back to your browser and refresh the page.

---

## If That Didn't Work

### Step 1: Kill All Python Processes
```bash
# Windows:
taskkill /F /IM python.exe

# Mac/Linux:
pkill -f python
pkill -f django
```

### Step 2: Clear Python Cache
```bash
# Delete cache folders
python -c "import shutil; shutil.rmtree('core/__pycache__', ignore_errors=True); shutil.rmtree('core/templatetags/__pycache__', ignore_errors=True); print('Cache cleared')"
```

### Step 3: Restart Server Fresh
```bash
python manage.py runserver
```

---

## If Using VS Code / PyCharm

### VS Code
1. Stop the debug session (red stop button)
2. Close the terminal
3. Open new terminal
4. Run: `python manage.py runserver`
5. Click the URL to open browser

### PyCharm
1. Click the stop button (red square)
2. Press Shift+F10 to rebuild and run
3. Or: Run → Run 'Django Server'

---

## If Using Docker

```bash
docker-compose down
docker-compose up
```

---

## Verify It's Working

After restart, check:
1. Go to: http://localhost:8000/customer/dashboard/
2. Look for **Grand Total** box (orange)
3. Check amounts show with commas (₱1,234.56)

If you see these, it's working! ✅

---

## What We Changed

We added:
- **Folder:** `core/templatetags/`
- **Files:**
  - `core/templatetags/__init__.py`
  - `core/templatetags/currency_filters.py`
- **Templates updated:** 10+ files with `{% load currency_filters %}`

Django needs to restart to discover these new files.

---

## Still Not Working?

Check that these 3 files exist:

**1. core/templatetags/__init__.py** - Should be empty (0 bytes)
```
✅ File exists
✅ Can be completely empty
```

**2. core/templatetags/currency_filters.py** - Should have our filter code
```
✅ File exists
✅ Has currency_format function
✅ Has sum_total function
```

**3. Your template has load tag** - Check your template file
```
{% load currency_filters %}  ← Must be near the top
```

If all 3 are present and server is restarted, it will work!

---

## Test Command (Optional)

Test the filter directly:
```bash
python manage.py shell
>>> from core.templatetags.currency_filters import currency_format
>>> currency_format(1234.56)
'1,234.56'
>>> exit()
```

If you see `'1,234.56'` output, the filter is installed correctly!

---

**Summary: Just restart Django server and refresh browser** ✅
