# Notification & Archival System - Visual Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     AVOCARBON PRICING APP                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────────────── FRONTEND ──────────────────────────┐  │
│  │                                                              │  │
│  │  Navbar with Notification Bell (🔔)                         │  │
│  │  └── NotificationsDropdown                                  │  │
│  │      ├── Unread Count Badge (red)                           │  │
│  │      ├── Last 50 Notifications                              │  │
│  │      │   ├── Approved (green)                               │  │
│  │      │   ├── Rejected (red)                                 │  │
│  │      │   ├── Escalated (yellow)                             │  │
│  │      │   └── New Comment (blue)                             │  │
│  │      ├── Mark as Read / Mark All Read                       │  │
│  │      └── Click → Navigate to Request                        │  │
│  │                                                              │  │
│  │  Archive Pages                                              │  │
│  │  ├── /pl/archived (PL decisions)                            │  │
│  │  │   └── Shows APPROVED_BY_PL, REJECTED_BY_PL,             │  │
│  │  │       APPROVED_BY_VP, REJECTED_BY_VP                     │  │
│  │  └── /vp/archived (VP decisions)                            │  │
│  │      └── Shows APPROVED_BY_VP, REJECTED_BY_VP               │  │
│  │                                                              │  │
│  │  Request Details (with Comments)                            │  │
│  │  └── CommentsThread (shown for approved requests)           │  │
│  │      ├── Active Tab (current comments)                      │  │
│  │      └── Archive Tab (archived comments)                    │  │
│  │                                                              │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                   │
│  ┌───────────────────── API LAYER ───────────────────────────────┐  │
│  │                                                              │  │
│  │  Notification Endpoints                                     │  │
│  │  ├── GET /api/notifications/user/{email}                    │  │
│  │  ├── GET /api/notifications/user/{email}/unread             │  │
│  │  ├── PATCH /api/notifications/{id}/read                     │  │
│  │  ├── PATCH /api/notifications/user/{email}/read-all         │  │
│  │  └── DELETE /api/notifications/{id}                         │  │
│  │                                                              │  │
│  │  Archive Endpoints                                          │  │
│  │  ├── GET /api/pricing-requests/pl/archived                  │  │
│  │  └── GET /api/pricing-requests/vp/archived                  │  │
│  │                                                              │  │
│  │  Decision Endpoints (modified)                              │  │
│  │  ├── POST /pl-decisions/{id}                                │  │
│  │  │   └── Creates notification on decision                   │  │
│  │  └── POST /vp-decisions/{id}                                │  │
│  │      └── Creates notification on decision                   │  │
│  │                                                              │  │
│  │  Comment Endpoints (modified)                               │  │
│  │  ├── POST /api/comments/request/{id}                        │  │
│  │  │   └── Creates notifications for relevant parties         │  │
│  │  └── GET /api/comments/request/{id}                         │  │
│  │                                                              │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                   │
│  ┌──────────────── BACKEND DATABASE ──────────────────────────┐  │
│  │                                                              │  │
│  │  tables:                                                    │  │
│  │  ├── pricing_requests (existing)                            │  │
│  │  ├── comments                                               │  │
│  │  │   └── + is_archived column (new)                         │  │
│  │  ├── notifications (new)                                    │  │
│  │  │   ├── id                                                 │  │
│  │  │   ├── recipient_email / recipient_role                   │  │
│  │  │   ├── request_id (FK)                                    │  │
│  │  │   ├── type (NotificationType enum)                       │  │
│  │  │   ├── title / message                                    │  │
│  │  │   ├── triggered_by (email & name)                        │  │
│  │  │   ├── is_read                                            │  │
│  │  │   ├── action_url                                         │  │
│  │  │   └── created_at / updated_at                            │  │
│  │  └── indexes:                                               │  │
│  │      ├── idx_notifications_recipient_email                  │  │
│  │      ├── idx_notifications_type                             │  │
│  │      ├── idx_notifications_request_id                       │  │
│  │      ├── idx_notifications_is_read                          │  │
│  │      ├── idx_notifications_created_at                       │  │
│  │      └── idx_comments_is_archived                           │  │
│  │                                                              │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

## Event Flow

### Scenario 1: Commercial Submits Request → PL Approves → Commercial Notified

```
Commercial User
    │
    ├─→ POST /api/pricing-requests
    │   └─→ Request Created (status: UNDER_REVIEW_PL)
    │
    └─→ Dashboard updated

PL User
    │
    ├─→ GET /pl (inbox)
    │   └─→ Sees pending request
    │
    ├─→ POST /pl-decisions/{request_id}
    │   ├─→ Request status updated (status: APPROVED_BY_PL)
    │   ├─→ create_pl_decision_notification()
    │   │   └─→ INSERT notification (type: PL_APPROVED)
    │   └─→ Email sent to commercial
    │
    └─→ Request added to archive

Commercial User
    │
    ├─→ Notification Bell 🔔 Updates
    │   ├─→ Unread count: 0 → 1
    │   └─→ Dropdown shows "Project X - PL Approved"
    │
    ├─→ Click Notification
    │   └─→ Navigate to /pricing-requests/{id}
    │
    └─→ CommentsThread now available (was hidden before approval)
```

### Scenario 2: Commercial Comments → PL/VP Notified

```
Commercial User
    │
    ├─→ POST /api/comments/request/{id}
    │   ├─→ Comment created
    │   ├─→ create_comment_notification()
    │   │   ├─→ Notify PL (if COMMERCIAL commented)
    │   │   ├─→ Notify VP (if escalated & COMMERCIAL commented)
    │   │   └─→ Notify COMMERCIAL (if PL/VP commented)
    │   └─→ commit to database
    │
    └─→ Comment appears in thread

PL User
    │
    ├─→ Notification Bell Updates
    │   └─→ "Commercial user commented on Project X"
    │
    ├─→ GET /pl/archived
    │   └─→ See completed decisions with discussion link
    │
    └─→ Click "View Discussion"
        └─→ Navigate to CommentsThread
```

### Scenario 3: PL Escalates → VP Reviews → VP Approves

```
PL User
    │
    ├─→ POST /pl-decisions/{request_id}
    │   ├─→ action: ESCALATE
    │   ├─→ Status: ESCALATED_TO_VP
    │   └─→ Email sent to VP
    │
    └─→ Appears in PL archive

VP User
    │
    ├─→ GET /vp (inbox)
    │   └─→ See escalated request
    │
    ├─→ Can add comments (CommentsThread)
    │   └─→ Notifications sent to COMMERCIAL & PL
    │
    ├─→ POST /vp-decisions/{request_id}
    │   ├─→ action: APPROVE
    │   ├─→ Status: APPROVED_BY_VP
    │   ├─→ create_vp_decision_notification()
    │   │   └─→ INSERT notification (type: VP_APPROVED)
    │   └─→ Email sent to commercial
    │
    └─→ Request moved to VP archive

Commercial User
    │
    ├─→ Notification Bell Updates
    │   └─→ "VP Approved - Final Price: $X"
    │
    └─→ Can still view discussion history
```

## Notification Color Coding

```
┌─────────────────────┬──────────┬────────────────────┐
│ Notification Type   │ Color    │ Background         │
├─────────────────────┼──────────┼────────────────────┤
│ PL_APPROVED         │ Green    │ #f0fdf4 (very lt) │
│ VP_APPROVED         │ Green    │ #f0fdf4 (very lt) │
│ PL_REJECTED         │ Red      │ #fef2f2 (very lt) │
│ VP_REJECTED         │ Red      │ #fef2f2 (very lt) │
│ PL_ESCALATED        │ Orange   │ #fef3c7 (very lt) │
│ NEW_COMMENT         │ Blue     │ #f0f9ff (very lt) │
│ REQUEST_SUBMITTED   │ Gray     │ #f9fafb (default) │
└─────────────────────┴──────────┴────────────────────┘
```

## User Journeys

### PL Manager's Journey
```
1. Login as PL (pl@avocarbon.com)
2. Dashboard → See stats
3. Navigation: "PL Inbox" → View pending requests
4. Click request → Review details & comments
5. Add comment (notifies COMMERCIAL)
6. Make decision: Approve/Reject/Escalate
7. Notification created → COMMERCIAL notified
8. Navigation: "Archived" → View past decisions
9. Click "View Discussion" → Access comment thread
10. Navbar bell 🔔 → See new comments from COMMERCIAL
```

### VP Manager's Journey
```
1. Login as VP (vp@avocarbon.com)
2. Dashboard → See stats
3. Navigation: "VP Inbox" → View escalated requests
4. Click request → See PL's recommendation + comments
5. Add comment (notifies COMMERCIAL & PL)
6. Make decision: Approve/Reject
7. Notification created → COMMERCIAL notified
8. Navigation: "Archived" → View all decisions made
9. Filter: Approved/Rejected
10. Navbar bell 🔔 → See updates from COMMERCIAL/PL
```

### Commercial User's Journey
```
1. Login as COMMERCIAL (user@avocarbon.com)
2. Dashboard → See my requests
3. Click "Create Request" → Submit new request
4. Navigate: "My Requests" → Track status
5. Once APPROVED → CommentsThread unlocked
6. Add comment (notifies PL/VP)
7. Receive notifications:
   ├── PL Decision: Approved/Rejected/Escalated
   ├── VP Decision: Final approval/rejection
   └── Comments: PL/VP response to my comments
8. Navbar bell 🔔 → Always see latest updates
9. Can discuss updates even after approval
```

## Database Schema

### notifications table
```
Column                  Type          Constraints
──────────────────────────────────────────────────
id                      INT           PRIMARY KEY
recipient_email         VARCHAR       NOT NULL, INDEX
recipient_role          VARCHAR       NOT NULL
request_id              INT           FK → pricing_requests
type                    VARCHAR       NOT NULL, INDEX (Enum)
title                   VARCHAR       NOT NULL
message                 TEXT          NOT NULL
triggered_by_email      VARCHAR       NOT NULL
triggered_by_name       VARCHAR       NOT NULL
is_read                 BOOLEAN       DEFAULT FALSE, INDEX
action_url              VARCHAR       NULLABLE
created_at              DATETIME      DEFAULT NOW(), INDEX
updated_at              DATETIME      DEFAULT NOW()

Indexes:
  - idx_notifications_recipient_email
  - idx_notifications_type
  - idx_notifications_request_id
  - idx_notifications_is_read
  - idx_notifications_created_at
```

### comments table (modified)
```
Existing columns:
  - id, request_id, author_email, author_name, author_role, content, created_at

New column:
  - is_archived BOOLEAN DEFAULT FALSE NOT NULL (INDEX)
```

## Performance Optimizations

1. **Indexes on Notifications**
   - `recipient_email` - Quick lookup for user notifications
   - `type` - Filter by notification type
   - `request_id` - Find notifications for a request
   - `is_read` - Unread count queries
   - `created_at` - Sort by date

2. **Pagination Ready**
   - Dropdown loads last 50 notifications (configurable)
   - Could add pagination to archive views

3. **Auto-refresh**
   - Unread count refreshes every 10 seconds
   - Full list refreshes only when dropdown opens
   - Reduces unnecessary API calls

## Security Considerations

1. **Role-Based Access Control**
   - Commercial can only see their own requests
   - PL only sees their assigned requests
   - VP only sees escalated requests
   - Archive views filtered by user email

2. **Email Verification**
   - Notifications tied to @avocarbon.com emails
   - Comments limited to authenticated users

3. **Data Privacy**
   - Comment content visible only to relevant parties
   - Notification content sanitized (first 100 chars preview)

## Notification Types (9 total)

| Type | Recipient | Trigger | Action |
|------|-----------|---------|--------|
| REQUEST_SUBMITTED | PL | Commercial submits | View request |
| PL_APPROVED | Commercial | PL approves | View discussion |
| PL_REJECTED | Commercial | PL rejects | View reason |
| PL_ESCALATED | VP | PL escalates | Review request |
| VP_APPROVED | Commercial | VP approves | View final price |
| VP_REJECTED | Commercial | VP rejects | View reason |
| NEW_COMMENT | PL/VP/Commercial | New comment | View thread |
| COMMENT_REPLY | Recipient | Reply (future) | View thread |
| REQUEST_CLOSED | All | Request closed (future) | View summary |
