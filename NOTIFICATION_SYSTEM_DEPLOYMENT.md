# Notification & Archival System - Deployment Checklist

## Completed Implementation

### ✅ Backend Notification Infrastructure
- **Model**: `backend/app/models/notification.py` - Complete Notification model with NotificationType enum
- **Schema**: `backend/app/schemas/notification.py` - Pydantic response schema
- **Router**: `backend/app/routers/notifications.py` - 5 REST endpoints for notification CRUD
- **Utils**: `backend/app/utils/notifications.py` - Helper functions for creating notifications
- **Integration**: Updated `backend/app/main.py` to register notification router and model

### ✅ Frontend Notification UI
- **Component**: `frontend/src/components/NotificationsDropdown.tsx`
  - Bell icon button with unread badge
  - Dropdown showing last 50 notifications
  - Color-coded notifications by type
  - Mark as read / Mark all as read functionality
  - Timestamps on all notifications
  - Auto-refresh every 10 seconds

- **Navbar Integration**: Updated `frontend/src/components/Navbar.tsx`
  - Added NotificationsDropdown to header
  - Displays unread count badge in red
  - Positioned before user email/logout button

### ✅ Decision Notification Creation
- **PL Decisions**: Updated `backend/app/routers/pl_decisions.py`
  - Creates notifications when PL approves/rejects/escalates requests
  - Sends to commercial requester
  
- **VP Decisions**: Updated `backend/app/routers/vp_decisions.py`
  - Creates notifications when VP approves/rejects escalated requests
  - Sends to commercial requester

### ✅ Comment Notification Creation
- **Comments Router**: Updated `backend/app/routers/comments.py`
  - Creates notifications when new comments are added
  - Notifies relevant parties:
    - PL notified when commercial comments
    - VP notified when commercial comments (on escalated requests)
    - Commercial notified when PL/VP comment

### ✅ Archived Requests Management
- **PL Archive View**: `frontend/src/pages/pl/PLArchived.tsx`
  - Shows all decisions made by PL (approved/rejected by PL or VP)
  - Filters: All, Approved, Rejected
  - Table with costing #, project, customer, prices, status, decision date
  - "View Discussion" button to access comment threads

- **VP Archive View**: `frontend/src/pages/vp/VPArchived.tsx`
  - Shows all VP decisions (approved/rejected by VP)
  - Same filter and table structure as PL archive
  - Displays VP suggested price and decision date

- **Backend Endpoints**: Updated `backend/app/routers/pricing_request.py`
  - `GET /api/pricing-requests/pl/archived?pl_email=...` - PL archived requests
  - `GET /api/pricing-requests/vp/archived?vp_email=...` - VP archived requests

### ✅ Router Updates
- Updated `frontend/src/router/index.tsx`
  - Added routes for `/pl/archived` → PLArchived component
  - Added routes for `/vp/archived` → VPArchived component
  - Added routes for `/pl/decision/:id` and `/vp/decision/:id` for discussion access

- Updated Navbar navigation links
  - PL users see: Dashboard, PL Inbox, Archived
  - VP users see: Dashboard, VP Inbox, Archived
  - Commercial users see: Dashboard, Create Request, My Requests

## Database Changes Required

Run this SQL to add the missing column for comment archiving:

```sql
ALTER TABLE comments ADD COLUMN is_archived BOOLEAN DEFAULT FALSE NOT NULL;
CREATE INDEX idx_comments_is_archived ON comments(is_archived);
```

The `notifications` table will be auto-created by SQLAlchemy when the app starts.

## API Endpoints Created

### Notifications API
- `GET /api/notifications/user/{user_email}` - Get 50 most recent notifications
- `GET /api/notifications/user/{user_email}/unread` - Get unread count
- `PATCH /api/notifications/{notification_id}/read` - Mark as read
- `PATCH /api/notifications/user/{user_email}/read-all` - Mark all as read
- `DELETE /api/notifications/{notification_id}` - Delete notification

### Archived Requests API
- `GET /api/pricing-requests/pl/archived?pl_email=...` - PL archived requests
- `GET /api/pricing-requests/vp/archived?vp_email=...` - VP archived requests

## Notification Types

The system supports 9 notification types:
- `REQUEST_SUBMITTED` - Initial request submitted
- `PL_APPROVED` - PL approves request
- `PL_REJECTED` - PL rejects request
- `PL_ESCALATED` - PL escalates to VP
- `VP_APPROVED` - VP approves escalated request
- `VP_REJECTED` - VP rejects escalated request
- `NEW_COMMENT` - New comment on discussion thread
- `COMMENT_REPLY` - Reply to comment (future use)
- `REQUEST_CLOSED` - Request closed/archived (future use)

## Testing Checklist

- [ ] Database migration executed (comments table updated)
- [ ] Backend server starts without errors
- [ ] Frontend compiles without TypeScript errors
- [ ] Notification bell icon appears in navbar
- [ ] Unread count badge displays correctly
- [ ] Notifications dropdown opens/closes on click
- [ ] Test PL decision → notification created and appears in dropdown
- [ ] Test VP decision → notification created and appears in dropdown
- [ ] Test comment → notification created for relevant parties
- [ ] Mark notification as read → badge updates
- [ ] Mark all as read → all notifications marked
- [ ] Click notification → navigates to request
- [ ] PL can see archived decisions at `/pl/archived`
- [ ] VP can see archived decisions at `/vp/archived`
- [ ] Archived requests show correct filters
- [ ] "View Discussion" button navigates to comment thread
- [ ] Archived requests table displays prices and dates correctly

## File Summary

**Backend Files Modified (8)**:
1. `app/models/notification.py` - NEW
2. `app/schemas/notification.py` - NEW
3. `app/routers/notifications.py` - NEW
4. `app/utils/notifications.py` - NEW
5. `app/main.py` - MODIFIED (2 changes)
6. `app/routers/pl_decisions.py` - MODIFIED
7. `app/routers/vp_decisions.py` - MODIFIED
8. `app/routers/comments.py` - MODIFIED
9. `app/routers/pricing_request.py` - MODIFIED (2 new endpoints)

**Frontend Files Modified (9)**:
1. `components/NotificationsDropdown.tsx` - NEW
2. `components/Navbar.tsx` - MODIFIED
3. `pages/pl/PLArchived.tsx` - NEW
4. `pages/vp/VPArchived.tsx` - NEW
5. `router/index.tsx` - MODIFIED (4 new routes)

**Total Files: 17 files modified/created**

## Key Features Summary

1. **Real-time Notifications**
   - Bell icon with unread badge in navbar
   - Dropdown with last 50 notifications
   - Auto-refreshes every 10 seconds
   - Color-coded by notification type
   - One-click access to related request

2. **Automatic Notification Creation**
   - When PL makes a decision → Commercial gets notified
   - When VP makes a decision → Commercial gets notified
   - When new comment posted → Relevant parties notified

3. **Archived Requests Management**
   - PL can view all their decisions (approved/rejected)
   - VP can view all their decisions
   - Filter by status (All/Approved/Rejected)
   - Access to comment discussions from archive

4. **Comment Threading**
   - Approved requests show comment section
   - Role-based color coding (Commercial, PL, VP)
   - Archive/Restore/Delete capabilities
   - Active/Archive tabs for organization

## Next Steps for User

1. **Execute Database Migration**
   ```sql
   ALTER TABLE comments ADD COLUMN is_archived BOOLEAN DEFAULT FALSE NOT NULL;
   CREATE INDEX idx_comments_is_archived ON comments(is_archived);
   ```

2. **Restart Backend**
   - Kill current backend process
   - Restart FastAPI app: `python -m uvicorn app.main:app --reload --port 5002`

3. **Verify Frontend**
   - Frontend should compile without errors
   - Test notification flow end-to-end

4. **Test Scenarios**
   - Create a pricing request → Should appear in dashboards
   - PL approves → Commercial gets notification
   - Click notification → Should navigate to discussion
   - View archived decisions → Should show decision details

## Notes

- Notification dropdown refreshes every 10 seconds (configurable in NotificationsDropdown.tsx line 38)
- Notifications are stored in PostgreSQL, persisting across sessions
- Comment archiving requires the is_archived column in the comments table
- All role-based access control is maintained (COMMERCIAL, PL, VP)
- Frontend uses Axios for API calls configured to `http://127.0.0.1:5002`
