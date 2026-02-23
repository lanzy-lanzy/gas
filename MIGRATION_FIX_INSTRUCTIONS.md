# Migration Fix & Application Instructions

## Current Status
- ✅ All code changes implemented
- ✅ Migration file created (0007_order_delivery_person_name.py)
- ✅ Migration conflict resolved
- ⚠️ reportlab compatibility issue blocking migration

## Issue: reportlab ImportError

When running `python manage.py migrate`, you may see:
```
ImportError: cannot import name 'getStringIO' from 'reportlab.lib.utils'
```

This is a compatibility issue between reportlab and xhtml2pdf versions.

## Solution: Fix reportlab Compatibility

### Option 1: Update reportlab to Compatible Version (Recommended)

```bash
pip install --upgrade reportlab==3.6.12
```

Then retry migration:
```bash
python manage.py migrate
```

### Option 2: Update pyproject.toml (Permanent Fix)

Edit `pyproject.toml`:

**Current:**
```toml
dependencies = [
    "django>=4.2.25",
    "django-shortcuts>=1.6",
    "pillow>=11.3.0",
    "reportlab>=4.4.4",
    "xhtml2pdf>=0.2.17",
]
```

**Change to:**
```toml
dependencies = [
    "django>=4.2.25",
    "django-shortcuts>=1.6",
    "pillow>=11.3.0",
    "reportlab==3.6.12",
    "xhtml2pdf>=0.2.17",
]
```

Then:
```bash
pip install --upgrade -r requirements.txt
python manage.py migrate
```

### Option 3: Use uv (if using uv package manager)

```bash
uv pip install reportlab==3.6.12
python manage.py migrate
```

## Complete Step-by-Step Instructions

### Step 1: Fix reportlab (Choose ONE option above)

**Option 1A - Using pip:**
```bash
cd D:\PrycegasStation
pip install --upgrade reportlab==3.6.12
```

**Option 1B - Using uv:**
```bash
cd D:\PrycegasStation
uv pip install reportlab==3.6.12
```

### Step 2: Verify Django Setup
```bash
cd D:\PrycegasStation
python manage.py check
```

Expected output:
```
System check identified no issues (0 silenced).
```

### Step 3: Show Migration Plan
```bash
python manage.py migrate --plan
```

Expected to show:
```
Planned operations:
  core.0007_order_delivery_person_name: Create model
```

### Step 4: Apply Migrations
```bash
python manage.py migrate
```

Expected output:
```
Running migrations:
  Applying core.0007_order_delivery_person_name... OK
```

### Step 5: Verify Migration Applied
```bash
python manage.py showmigrations core | findstr "0007"
```

Should show:
```
[X] 0007_order_delivery_person_name
```

## Troubleshooting

### If you still get ImportError:

1. **Clear Python cache:**
```bash
python -Bc "import compileall; compileall.compile_dir('.')"
```

2. **Remove __pycache__:**
```bash
cd D:\PrycegasStation
for /r %i in (__pycache__) do rd /s /q %i
```

3. **Try again:**
```bash
python manage.py migrate
```

### If you get "conflicting migrations":

The issue should be resolved since we deleted 0002_order_delivery_person_name and created 0007_order_delivery_person_name instead.

If you still see it:
```bash
python manage.py showmigrations core
```

Look for duplicate 0002 files and delete the conflicting one manually.

### If migration shows as "unapplied":

```bash
# Check current state
python manage.py migrate --plan

# Apply specific migration
python manage.py migrate core 0007
```

## Verification Steps

### Step 1: Check Database Column Exists
```bash
python manage.py dbshell
```

Then in the SQL shell:
```sql
.schema core_order
```

Look for the `delivery_person_name` column.

### Step 2: Check Django ORM
```bash
python manage.py shell
```

Then:
```python
from core.models import Order
order = Order.objects.first()
print(hasattr(order, 'delivery_person_name'))  # Should be True
print(hasattr(order, 'get_delivery_person'))  # Should be True
```

### Step 3: Test in Admin
```bash
python manage.py runserver
```

Navigate to: http://localhost:8000/admin/core/order/

You should see the `delivery_person_name` field in the Order form.

### Step 4: Test in Customer View
1. Login as a customer
2. Go to order detail page
3. Verify the order information displays correctly
4. Check that "Processed/Delivered By" section displays (if data set)

## Commands Summary

```bash
# 1. Fix reportlab
pip install --upgrade reportlab==3.6.12

# 2. Verify setup
python manage.py check

# 3. Show plan
python manage.py migrate --plan

# 4. Apply migrations
python manage.py migrate

# 5. Verify
python manage.py showmigrations core | findstr "0007"
```

## Expected Results After Migration

### In Database:
- New column: `delivery_person_name VARCHAR(100) DEFAULT ''`
- No data loss
- Fully reversible

### In Django Admin:
- Order edit form shows new field
- Can set "Processed by" (existing)
- Can set "Delivery Person Name" (new)

### In Customer View:
- Order detail page shows processor info
- Shows delivery person if set
- Shows cashier if set

### In Model:
- `order.delivery_person_name` - access field directly
- `order.get_delivery_person` - property returns delivery person name
- `order.processed_by_name` - property returns processor name

## If Migration Fails

### Rollback (if needed):
```bash
python manage.py migrate core 0006
```

This reverts to the previous state without breaking anything.

### Start Fresh:
```bash
# Delete migration
del core\migrations\0007_order_delivery_person_name.py

# Recreate
python manage.py makemigrations core

# Apply
python manage.py migrate
```

## After Migration - Next Steps

1. ✅ Test in admin interface
2. ✅ Edit an order and set both fields
3. ✅ View order as customer
4. ✅ Verify information displays
5. ✅ Test with None values
6. ✅ Update order processing flows to populate fields
7. ✅ Consider adding to email notifications

## Quick Checklist

- [ ] Fixed reportlab compatibility
- [ ] Ran `python manage.py check` successfully
- [ ] Ran `python manage.py migrate` successfully
- [ ] Verified migration in database
- [ ] Tested in Django admin
- [ ] Tested in customer order view
- [ ] Data displays correctly
- [ ] Documentation complete

## Support

If you encounter issues:

1. Check the pyproject.toml file to ensure reportlab is correct
2. Verify Python path: `python --version` (should be 3.8+)
3. Check Django version: `python -c "import django; print(django.VERSION)"`
4. Review this guide section by section
5. Look for hidden __pycache__ directories causing import issues

## Notes

- The migration file is location-independent (just needs to run once)
- Safe to run multiple times (Django tracks applied migrations)
- Fully reversible if needed
- No production data is modified
