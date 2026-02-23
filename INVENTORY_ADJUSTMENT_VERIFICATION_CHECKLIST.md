# Inventory Adjustment - Verification Checklist

## Pre-Deployment Checks

### Database & Models
- [ ] Product table has active products with `is_active=True`
- [ ] InventoryAdjustment model exists and migrations applied
- [ ] StockMovement model exists and migrations applied
- [ ] User model properly configured
- [ ] Foreign keys properly set up

### Code Review
- [ ] `core/forms.py` - InventoryAdjustmentForm updated with adjustment_type and quantity fields
- [ ] `core/forms.py` - save() method converts adjustment_type + quantity to quantity_change
- [ ] `core/models.py` - InventoryAdjustment.save() validates and updates stock
- [ ] `core/views.py` - inventory_adjustment() view has error handling
- [ ] `templates/dealer/inventory_adjustment.html` - form displays correctly with radio buttons
- [ ] JavaScript in template updates projected stock in real-time

### Form Fields
- [ ] Product dropdown renders (via form.product)
- [ ] Adjustment Type radio buttons display ("Increase Stock" / "Decrease Stock")
- [ ] Quantity field accepts only positive integers
- [ ] Reason dropdown shows adjustment reasons
- [ ] Notes textarea displays
- [ ] All fields show proper error messages

### Form Behavior
- [ ] Form validates that all required fields filled
- [ ] Form prevents negative quantity values
- [ ] Form correctly converts adjustment_type + quantity to quantity_change
- [ ] Form.save(commit=False) returns object with quantity_change set
- [ ] Form.save(commit=True) creates database record

### View Behavior
- [ ] GET request shows blank form
- [ ] POST with invalid data shows form with error messages
- [ ] POST with valid data processes adjustment
- [ ] View checks quantity_change is set before proceeding
- [ ] View validates stock won't go negative
- [ ] View uses database transaction for atomic updates
- [ ] View shows success message with adjustment amount
- [ ] View redirects to inventory management on success

### Model Behavior
- [ ] InventoryAdjustment.save() validates quantity_change is set
- [ ] Model refreshes product from DB before updating
- [ ] Model calculates new stock correctly
- [ ] Model validates new stock won't be negative
- [ ] Model updates product.current_stock
- [ ] Model creates StockMovement record
- [ ] Model handles creation errors gracefully

### Stock Updates
- [ ] INCREASE adjustment adds to stock
- [ ] DECREASE adjustment subtracts from stock
- [ ] Stock is accurate in database
- [ ] Product updated_at timestamp changes
- [ ] Stock visible in inventory management view

### Audit Trail
- [ ] StockMovement record created for each adjustment
- [ ] StockMovement shows correct previous_stock
- [ ] StockMovement shows correct new_stock
- [ ] StockMovement shows correct quantity change
- [ ] StockMovement tracks who made adjustment
- [ ] StockMovement tracks timestamp

### Error Handling
- [ ] No products error handled
- [ ] No active user error handled
- [ ] Negative stock prevented at all levels
- [ ] Invalid form data shows error messages
- [ ] Database errors show meaningful messages
- [ ] Exceptions logged to console

### Real-Time Features
- [ ] Product selection triggers stock fetch
- [ ] Quantity change updates projected stock
- [ ] Adjustment type change updates projected stock
- [ ] Reason selection enables/disables submit button
- [ ] Projected stock shows warning if negative

### Edge Cases
- [ ] Cannot select inactive products
- [ ] Cannot submit with empty quantity
- [ ] Cannot submit with quantity = 0
- [ ] Cannot submit with negative quantity
- [ ] Cannot result in negative stock
- [ ] Multiple concurrent adjustments handled

## User Testing Checklist

### Create INCREASE Adjustment
- [ ] Navigate to Inventory → Inventory Adjustment
- [ ] Select a product from dropdown
- [ ] Verify current stock displays
- [ ] Select "Increase Stock"
- [ ] Enter quantity (e.g., 10)
- [ ] Verify projected stock increases
- [ ] Select reason from dropdown
- [ ] (Optional) Add notes
- [ ] Click "Apply Adjustment"
- [ ] Verify success message shows "Stock adjusted by 10"
- [ ] Verify page redirects
- [ ] Verify stock increased in inventory view
- [ ] Verify adjustment history shows entry

### Create DECREASE Adjustment
- [ ] Navigate to Inventory → Inventory Adjustment
- [ ] Select same product
- [ ] Verify current stock shows new value
- [ ] Select "Decrease Stock"
- [ ] Enter quantity (e.g., 5)
- [ ] Verify projected stock decreases
- [ ] Select reason from dropdown
- [ ] Click "Apply Adjustment"
- [ ] Verify success message shows "Stock adjusted by -5"
- [ ] Verify stock decreased in inventory view

### Test Negative Stock Prevention
- [ ] Current stock is 20
- [ ] Try to decrease by 25
- [ ] Verify "cannot result in negative stock" message
- [ ] Verify button is disabled
- [ ] Try value of 20
- [ ] Verify "Stock adjusted by -20" (should work)
- [ ] Verify new stock is 0
- [ ] Try any decrease when stock is 0
- [ ] Verify prevention works

### Test Form Validation
- [ ] Leave product blank → shows "required" error
- [ ] Leave adjustment type blank → form invalid
- [ ] Leave quantity blank → shows "required" error
- [ ] Enter quantity = 0 → shows "greater than zero" error
- [ ] Enter quantity = -5 → form prevents submission
- [ ] Leave reason blank → shows "required" error
- [ ] Notes optional → can leave blank
- [ ] All fields filled → submit button enabled

### Test Real-Time Feedback
- [ ] Select product → current stock appears
- [ ] Enter quantity → projected stock updates
- [ ] Change adjustment type → projected stock updates
- [ ] Remove quantity → projected stock shows current value only
- [ ] Select increase then 30 (stock is 50) → projected should be 80
- [ ] Switch to decrease → projected should be 20
- [ ] Back to increase → projected should be 80

## Performance Checks

- [ ] Form loads quickly (< 1 second)
- [ ] Product dropdown loads all products
- [ ] Adjustment submission completes quickly (< 2 seconds)
- [ ] Page doesn't freeze during submission
- [ ] No N+1 queries in logs
- [ ] Database transactions complete successfully
- [ ] No memory leaks in form rendering

## Security Checks

- [ ] CSRF token present in form
- [ ] Only authenticated users can access
- [ ] Users can't see other users' adjustments
- [ ] Only active products can be selected
- [ ] Quantity_change validates at multiple levels
- [ ] No SQL injection possible
- [ ] No XSS possible in notes field

## Documentation Checks

- [ ] Code comments explain logic
- [ ] Variable names are clear
- [ ] Error messages are user-friendly
- [ ] Success messages confirm action taken
- [ ] Help text visible in form

## Final Production Checks

Before going live:

1. **Backup Database**
   - [ ] Full database backup created
   - [ ] Backup tested and restorable

2. **Code Review**
   - [ ] No debug print statements left
   - [ ] No test data in code
   - [ ] All imports present
   - [ ] No commented-out code
   - [ ] Proper formatting and indentation

3. **Browser Testing**
   - [ ] Works on Chrome
   - [ ] Works on Firefox
   - [ ] Works on Safari
   - [ ] Works on Edge
   - [ ] Responsive on mobile

4. **Log Monitoring**
   - [ ] No error logs on successful submission
   - [ ] Proper error logs on failures
   - [ ] No sensitive data in logs

5. **Database Verification**
   - [ ] InventoryAdjustment table is empty (or backup from prod)
   - [ ] StockMovement records consistent
   - [ ] No orphaned records
   - [ ] Foreign keys valid

## Sign-Off

- [ ] Forms work correctly
- [ ] Views process correctly
- [ ] Models save correctly
- [ ] Stock updates correctly
- [ ] Audit trail created
- [ ] Error handling complete
- [ ] User feedback clear
- [ ] Performance acceptable
- [ ] Security verified
- [ ] Ready for production

---

**Final Status**: _________________________
**Tested By**: _________________________
**Date**: _________________________
**Comments**: 
_________________________________________________
_________________________________________________

---

## Known Limitations / Future Improvements

- [ ] No file upload for damage photos
- [ ] No batch adjustment capability
- [ ] No adjustment approval workflow
- [ ] No scheduled adjustments
- [ ] No email notifications
- [ ] No export to Excel
- [ ] No adjustment templates

