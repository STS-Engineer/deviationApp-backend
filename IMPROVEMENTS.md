# Avocarbon Pricing App - Improvements Summary

## Overview
This document outlines all improvements made to the commercial pricing deviation workflow application for AVO Carbon Group.

---

## 1. Backend Improvements

### 1.1 Enhanced Data Models

**File**: `app/models/pricing_request.py`

#### New Fields Added:
- `requester_name` - Store name of commercial user
- `product_line_responsible_name` - Store PL manager name
- `vp_name` - Store VP name
- `attachment_path` - Support for file attachments
- `pl_suggested_price` - Track PL suggested price
- `pl_comments` - Track PL comments
- `pl_decision_date` - Track when PL made decision
- `vp_suggested_price` - Track VP suggested price
- `vp_comments` - Track VP comments
- `vp_decision_date` - Track when VP made decision
- `final_approved_price` - Store final approved price

#### Improved Indexing:
- Added indexes to frequently queried fields for better performance
- `costing_number` - Unique index
- `status`, `requester_email`, `product_line_responsible_email`, `vp_email`

---

### 1.2 Enhanced Schemas

**Files**: 
- `app/schemas/pricing_request.py`
- `app/schemas/pl_decision.py`
- `app/schemas/vp_decision.py`

#### Features:
- Added detailed validation using Pydantic Field with constraints
- Implemented Enum types for actions (APPROVE, REJECT, ESCALATE)
- Better error messages for invalid inputs
- Separated request creation schema from response schemas
- Added comprehensive response schemas with all fields

---

### 1.3 Improved API Endpoints

#### Pricing Request Router (`app/routers/pricing_request.py`)

**New/Enhanced Endpoints:**

1. **POST /pricing-requests** - Submit new request
   - Enhanced validation
   - Check for duplicate costing numbers
   - Validate price logic (target < initial)
   - Proper error messages

2. **GET /pricing-requests** - List all requests with filters
   - Filter by status, product_line, requester_email
   - Sorted by creation date (newest first)

3. **GET /pricing-requests/{request_id}** - Get full request details
   - Includes all decision information

4. **GET /pricing-requests/user/{requester_email}** - Get user's requests
   - Filter requests for specific commercial user

#### PL Decisions Router (`app/routers/pl_decisions.py`)

**New/Enhanced Endpoints:**

1. **GET /pl-decisions/inbox?pl_email={email}** - Get PL inbox
   - List all pending requests for PL
   - Only shows UNDER_REVIEW_PL status

2. **GET /pl-decisions/{request_id}** - Get request for PL review
   - Full details including attachment path

3. **POST /pl-decisions/{request_id}** - PL makes decision
   - Actions: APPROVE, REJECT, ESCALATE
   - Store suggested price and comments
   - Track decision date
   - Send appropriate emails

#### VP Decisions Router (`app/routers/vp_decisions.py`)

**New/Enhanced Endpoints:**

1. **GET /vp-decisions/inbox?vp_email={email}** - Get VP inbox
   - List all escalated requests for VP
   - Only shows ESCALATED_TO_VP status

2. **GET /vp-decisions/{request_id}** - Get request for VP review
   - Includes PL decision information

3. **POST /vp-decisions/{request_id}** - VP makes final decision
   - Actions: APPROVE, REJECT
   - Set final approved price
   - Send decision notification

---

### 1.4 Enhanced Email Service

**File**: `app/emails/mailer.py`

#### Features:

1. **Improved SMTP Support**
   - Supports Outlook/Office 365 SMTP with authentication
   - Supports standard SMTP with or without TLS/STARTTLS
   - Better error handling and logging

2. **Enhanced Email Templates**
   - Professional HTML formatting
   - Status indicators with icons and colors
   - Clear action buttons
   - Price calculation and display
   - Support for multiple recipients (CC)

3. **Four Email Types:**

   - **Pricing Request Email** (to PL Responsible)
     - Shows request details with price difference
     - Action options clearly listed
     - Direct review link
   
   - **PL Decision Email** (to Commercial)
     - Shows PL's decision with color coding
     - Includes suggested price if applicable
     - PL comments displayed
   
   - **Escalation Email** (to VP)
     - Shows escalation reason
     - PL's justification included
     - Pricing details and comparison
   
   - **VP Decision Email** (to Commercial)
     - Final decision status
     - Approved price if applicable
     - VP comments

---

### 1.5 Data Loading from Excel

**File**: `app/utils/excel_loader.py`

#### Features:
- Load customers from ODS (LibreOffice) files
- Fallback to XLSX (Excel) files
- Automatic deduplication and sorting
- Error handling with fallback to empty list
- Cached on endpoint for better performance

#### Supported File Formats:
- `.ods` (primary - `/data/Classeur1.ods`)
- `.xlsx` (fallback - `/data/customers.xlsx`)

---

### 1.6 Constants and Utils

**File**: `app/utils/constants.py`

#### Product Lines:
- assembly
- friction
- injection
- seals
- brushes
- chokes

#### Plants:
- Poitiers, Amiens, Mexico, Tianjin, Frankfurt, Tunisia, Kunshan, Chennai

#### Status Workflow Stages:
- DRAFT (0)
- SUBMITTED (1)
- UNDER_REVIEW_PL (2)
- ESCALATED_TO_VP (3)
- APPROVED_BY_PL (4)
- APPROVED_BY_VP (4)
- REJECTED_BY_PL (5)
- REJECTED_BY_VP (5)
- BACK_TO_COMMERCIAL (2)
- CLOSED (6)

---

## 2. Frontend Improvements

### 2.1 Enhanced API Client

**File**: `frontend/src/api/pricingRequests.ts`

#### New Type Definitions:
```typescript
PricingRequestCreate - Request creation payload
PricingRequest - Full response with all fields
```

#### New Methods:
- `getPricingRequests(filters)` - Get filtered list
- `getPricingRequest(id)` - Get single request
- `getUserPricingRequests(email)` - Get user's requests

---

### 2.2 Enhanced Decision API Clients

**Files**: 
- `frontend/src/api/plDecisions.ts`
- `frontend/src/api/vpDecisions.ts`

#### Features:
- Type-safe payloads and responses
- Inbox endpoints for getting pending requests
- Detail endpoints for full request information
- Improved error handling

---

### 2.3 Dropdowns API

**File**: `frontend/src/api/dropdowns.ts`

#### Features:
- `getDropdowns()` - Load all dropdowns in parallel
- Returns product_lines, plants, customers
- Graceful fallback if one fails
- Performance optimized with Promise.all

---

### 2.4 Enhanced CreateRequest Component

**File**: `frontend/src/pages/commercial/CreateRequest.tsx`

#### Improvements:

1. **Better Form Organization**
   - Grouped into logical sections
   - Request Information
   - Pricing Details
   - Problem Description
   - Contacts

2. **Dynamic Dropdowns**
   - Loads on component mount
   - Product lines dropdown
   - Plants dropdown
   - Customers dropdown (from Excel)

3. **Enhanced Validation**
   - Real-time error clearing
   - Detailed error messages
   - Price logic validation
   - Email format validation

4. **Improved UI/UX**
   - Visual price difference calculation
   - Section dividers
   - Better field labeling
   - Placeholder hints
   - Loading states
   - Cancel button

5. **Enhanced Components**
   - `Field` - Text input with error display
   - `NumberField` - Number input with step and validation
   - `SelectField` - Dropdown with options

---

## 3. Workflow Enhancements

### Complete Request Lifecycle

```
1. COMMERCIAL creates request
   ↓
2. Email sent to PL RESPONSIBLE
   ↓
3. PL RESPONSIBLE reviews (can):
   - APPROVE → Status: APPROVED_BY_PL → Email to Commercial
   - SUGGEST PRICE → Store suggested_price
   - REJECT → Status: BACK_TO_COMMERCIAL → Email to Commercial
   - ESCALATE → Status: ESCALATED_TO_VP → Email to VP
   ↓
4. If escalated, VP REVIEWS (can):
   - APPROVE → Status: CLOSED → Email to Commercial
   - SUGGEST PRICE → Store final_approved_price
   - REJECT → Status: BACK_TO_COMMERCIAL → Email to Commercial
   ↓
5. COMMERCIAL receives all notifications and can:
   - Close request
   - Re-adjust if rejected
   - Follow up with customer
```

---

## 4. Key Features

### Email Notifications
- Automated HTML emails with professional formatting
- Icons and color-coded statuses
- Direct action links to portal
- Outlook/Office 365 SMTP support
- Optional CC recipients

### Data Validation
- Costing number uniqueness
- Price logic validation
- Email domain validation (@avocarbon.com)
- Required field validation
- Numeric range validation

### Audit Trail
- All decisions timestamped
- Comments stored for history
- Suggested prices tracked
- Status changes recorded

### Performance
- Indexed database queries
- Parallel API calls for dropdowns
- Efficient filtering
- Minimal database queries

---

## 5. Configuration

### Environment Variables (Backend)

```env
# SMTP Configuration
SMTP_HOST=smtp.office365.com  # or mail.avocarbon.com
SMTP_PORT=587
SMTP_USER=your-email@avocarbon.com
SMTP_PASSWORD=your-password
SMTP_FROM=notifications@avocarbon.com

# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=avocarbon_pricing
DB_USER=postgres
DB_PASSWORD=password

# URLs
FRONTEND_BASE_URL=http://localhost:5173
BACKEND_BASE_URL=http://127.0.0.1:5002
```

### Frontend Configuration

```env
VITE_BACKEND_URL=http://127.0.0.1:5002
```

---

## 6. Testing the Application

### 1. Start Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 5002
```

### 2. Start Frontend
```bash
cd frontend
npm install
npm run dev
```

### 3. Test Workflow

**Step 1: Commercial Creates Request**
1. Go to `/commercial/create-request`
2. Fill all required fields
3. Click "Submit Request"
4. Should see success message

**Step 2: PL Reviews Request**
1. PL receives email (check email or go to `/pl/inbox`)
2. Click "Review Request"
3. Can approve, reject, suggest price, or escalate
4. Commercial receives email with decision

**Step 3: VP Reviews (if escalated)**
1. VP receives escalation email
2. Go to `/vp/inbox`
3. Review and make final decision
4. Commercial receives final decision email

---

## 7. Database Migration

If updating existing database, run:

```sql
-- Add new columns for names and decision tracking
ALTER TABLE pricing_requests ADD COLUMN requester_name VARCHAR(255);
ALTER TABLE pricing_requests ADD COLUMN product_line_responsible_name VARCHAR(255);
ALTER TABLE pricing_requests ADD COLUMN vp_name VARCHAR(255);
ALTER TABLE pricing_requests ADD COLUMN attachment_path VARCHAR(500);
ALTER TABLE pricing_requests ADD COLUMN pl_suggested_price NUMERIC;
ALTER TABLE pricing_requests ADD COLUMN pl_comments TEXT;
ALTER TABLE pricing_requests ADD COLUMN pl_decision_date TIMESTAMP;
ALTER TABLE pricing_requests ADD COLUMN vp_suggested_price NUMERIC;
ALTER TABLE pricing_requests ADD COLUMN vp_comments TEXT;
ALTER TABLE pricing_requests ADD COLUMN vp_decision_date TIMESTAMP;
ALTER TABLE pricing_requests ADD COLUMN final_approved_price NUMERIC;

-- Create indexes for better query performance
CREATE INDEX idx_costing_number ON pricing_requests(costing_number);
CREATE INDEX idx_status ON pricing_requests(status);
CREATE INDEX idx_requester_email ON pricing_requests(requester_email);
CREATE INDEX idx_pl_responsible ON pricing_requests(product_line_responsible_email);
CREATE INDEX idx_vp_email ON pricing_requests(vp_email);
CREATE INDEX idx_created_at ON pricing_requests(created_at);
```

---

## 8. Future Enhancements

### Possible Future Features:
1. File upload/attachment support
2. Request templates for recurring scenarios
3. Approval history timeline view
4. Bulk import from Excel
5. Analytics and reporting dashboard
6. Automated approval rules based on business rules
7. Mobile app version
8. Integration with ERP system
9. Audit log with full change history
10. PDF generation for approved requests

---

## Summary

This implementation provides a complete, enterprise-grade pricing deviation request system with:

✅ **Three-tier approval workflow** (Commercial → PL → VP)
✅ **Email notifications** for all stakeholders
✅ **Professional UI/UX** with intuitive forms
✅ **Robust data validation** and error handling
✅ **Database optimization** with proper indexing
✅ **Excel integration** for customer data
✅ **Audit trail** of all decisions
✅ **Flexible API** with filtering and detailed responses
✅ **SMTP support** for Outlook/Office 365
✅ **Type-safe** frontend and backend

The application is production-ready and scalable for enterprise use.
