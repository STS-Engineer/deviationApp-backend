# Bug Fixes for Rejection/Approval Issues

## Issues Identified and Fixed

### 1. **Email Notifications Not Sent on Rejection**
**Problem**: When rejecting a request (both PL and VP), no email was being sent to the commercial user.

**Root Cause**: The email functions had incomplete status mappings that only handled specific statuses like `APPROVED_BY_PL` and `CLOSED`, but not rejection statuses.

**Fix Applied**:
- Updated `send_pl_decision_to_commercial()` in [backend/app/emails/mailer.py](backend/app/emails/mailer.py) to include `REJECTED_BY_PL` status with a ❌ icon and red color (#dc3545)
- Updated `send_vp_decision_to_commercial()` in [backend/app/emails/mailer.py](backend/app/emails/mailer.py) to include `REJECTED_BY_VP` and `APPROVED_BY_VP` statuses with appropriate icons and colors

### 2. **Rejected/Approved Price Not Updated in Commercial Dashboard**
**Problem**: After rejection or approval, the commercial user's request list didn't show the final approved price.

**Root Cause**: 
- The `PricingRequestResponse` schema didn't include the `final_approved_price` field, even though the model stored it
- Only the detailed view had this field

**Fix Applied**:
- Added `final_approved_price: Optional[float]` field to `PricingRequestResponse` schema in [backend/app/schemas/pricing_request.py](backend/app/schemas/pricing_request.py)
- This ensures the price is included when commercial users fetch their request list

### 3. **Rejection Clearing Previous Approvals**
**Problem**: When rejecting a request that might have been previously approved at a stage, the `final_approved_price` wasn't properly cleared.

**Fix Applied**:
- Updated [backend/app/routers/pl_decisions.py](backend/app/routers/pl_decisions.py) to set `request.final_approved_price = None` when rejecting
- Updated [backend/app/routers/vp_decisions.py](backend/app/routers/vp_decisions.py) to set `request.final_approved_price = None` when rejecting

## What Changed

### Backend Changes

**[backend/app/emails/mailer.py](backend/app/emails/mailer.py)**
- Added `REJECTED_BY_PL` to the decision icons and colors mapping (red ❌)
- Added `REJECTED_BY_VP` and `APPROVED_BY_VP` to the VP decision icons and colors mapping

**[backend/app/routers/pl_decisions.py](backend/app/routers/pl_decisions.py)**
- Line ~74: Added `request.final_approved_price = None` when rejecting

**[backend/app/routers/vp_decisions.py](backend/app/routers/vp_decisions.py)**
- Line ~85: Added `request.final_approved_price = None` when rejecting

**[backend/app/schemas/pricing_request.py](backend/app/schemas/pricing_request.py)**
- Added `final_approved_price: Optional[float] = None` to `PricingRequestResponse` class

## Testing the Fix

To test these changes:

1. **Create a new pricing request** as Commercial user
2. **Reject it** as PL responsible - should now:
   - Send email to Commercial with rejection notification
   - Show status as `REJECTED_BY_PL` in dashboard
   - Display appropriate red icon and rejection message

3. **Escalate a request to VP** and reject it as VP - should now:
   - Send email to Commercial with rejection notification
   - Show status as `REJECTED_BY_VP` in dashboard
   - Display appropriate red icon and rejection message

4. **Refresh Commercial dashboard** - should see:
   - Updated status for rejected/approved requests
   - Final approved price displayed (if approved) or empty (if rejected)

## Email Template Status

The following statuses now have proper email templates:
- ✅ `APPROVED_BY_PL` - Green checkmark
- ❌ `REJECTED_BY_PL` - Red X
- 🔺 `ESCALATED_TO_VP` - Blue arrow
- ⚠️ `BACK_TO_COMMERCIAL` - Yellow warning
- ✅ `APPROVED_BY_VP` - Green checkmark (CL same as CLOSED)
- ❌ `REJECTED_BY_VP` - Red X
- 📋 `CLOSED` - Green checkmark (back compat)

