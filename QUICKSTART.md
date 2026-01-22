# Quick Start Guide - Avocarbon Pricing App

## Prerequisites

- Python 3.9+
- Node.js 16+
- PostgreSQL 12+
- Git

## Installation Steps

### 1. Clone the Repository

```bash
cd avocarbon-pricing-app
```

### 2. Backend Setup

#### Install Python Dependencies

```bash
cd backend
python -m venv venv

# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

#### Configure Database

```bash
# Create PostgreSQL database
createdb avocarbon_pricing

# Or use your database management tool
```

#### Environment Configuration

```bash
# Copy and edit the .env file
cp .env.example .env

# Edit .env with your settings:
# - DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD
# - SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, SMTP_FROM
```

#### Run Database Migrations

The app creates tables automatically on startup. If you need to add new columns to existing database:

```sql
-- Add new columns for enhanced tracking
ALTER TABLE pricing_requests ADD COLUMN IF NOT EXISTS requester_name VARCHAR(255);
ALTER TABLE pricing_requests ADD COLUMN IF NOT EXISTS product_line_responsible_name VARCHAR(255);
ALTER TABLE pricing_requests ADD COLUMN IF NOT EXISTS vp_name VARCHAR(255);
ALTER TABLE pricing_requests ADD COLUMN IF NOT EXISTS attachment_path VARCHAR(500);
ALTER TABLE pricing_requests ADD COLUMN IF NOT EXISTS pl_suggested_price NUMERIC;
ALTER TABLE pricing_requests ADD COLUMN IF NOT EXISTS pl_comments TEXT;
ALTER TABLE pricing_requests ADD COLUMN IF NOT EXISTS pl_decision_date TIMESTAMP;
ALTER TABLE pricing_requests ADD COLUMN IF NOT EXISTS vp_suggested_price NUMERIC;
ALTER TABLE pricing_requests ADD COLUMN IF NOT EXISTS vp_comments TEXT;
ALTER TABLE pricing_requests ADD COLUMN IF NOT EXISTS vp_decision_date TIMESTAMP;
ALTER TABLE pricing_requests ADD COLUMN IF NOT EXISTS final_approved_price NUMERIC;
```

#### Start Backend Server

```bash
# Make sure you're in the backend directory with venv activated
uvicorn app.main:app --reload --port 5002

# You should see:
# INFO:     Uvicorn running on http://127.0.0.1:5002
# INFO:     Application startup complete
```

### 3. Frontend Setup

#### Install Node Dependencies

```bash
cd frontend
npm install
```

#### Environment Configuration

```bash
# The frontend is configured to use http://127.0.0.1:5002 by default
# You can change this in .env:
echo "VITE_BACKEND_URL=http://127.0.0.1:5002" > .env
```

#### Start Frontend Development Server

```bash
npm run dev

# You should see:
# VITE v4.x.x  ready in 200 ms
# ➜  Local:   http://localhost:5173/
```

---

## Testing the Application

### 1. Open Browser

Navigate to: **http://localhost:5173**

### 2. Test Commercial Flow

1. Go to `/commercial/create-request`
2. Fill in the form:
   - **Costing Number**: PCC-2024-001
   - **Project Name**: Test Project
   - **Customer**: Customer A
   - **Product Line**: assembly
   - **Plant**: Poitiers
   - **Yearly Sales**: 50000
   - **Initial Price**: 100
   - **Target Price**: 75
   - **Problem to Solve**: Customer negotiation
   - **Requester Email**: commercial@avocarbon.com
   - **Requester Name**: John Doe
   - **PL Responsible Email**: pl.manager@avocarbon.com
   - **VP Email** (optional): vp@avocarbon.com

3. Click "Submit Request"
4. Should see success message

### 3. Test PL Flow

1. Email is sent to pl.manager@avocarbon.com (check email or logs)
2. Go to `/pl/inbox`
3. Click on the request
4. Can:
   - Approve the price
   - Suggest alternative price
   - Add comments
   - Reject
   - Escalate to VP

### 4. Test VP Flow (if escalated)

1. Email is sent to vp@avocarbon.com
2. Go to `/vp/inbox`
3. Click on the request
4. Can:
   - Approve the price
   - Suggest alternative price
   - Add comments
   - Reject

### 5. Commercial Receives Decision

1. Commercial gets email with decision
2. Can review in `/commercial/my-requests`

---

## API Documentation

### Available Endpoints

#### Pricing Requests
- `POST /pricing-requests` - Submit new request
- `GET /pricing-requests` - List all requests (filters: status, product_line, requester_email)
- `GET /pricing-requests/{id}` - Get request details
- `GET /pricing-requests/user/{email}` - Get user's requests

#### PL Decisions
- `GET /pl-decisions/inbox?pl_email={email}` - Get PL inbox
- `POST /pl-decisions/{request_id}` - Submit PL decision
- `GET /pl-decisions/{request_id}` - Get request for review

#### VP Decisions
- `GET /vp-decisions/inbox?vp_email={email}` - Get VP inbox
- `POST /vp-decisions/{request_id}` - Submit VP decision
- `GET /vp-decisions/{request_id}` - Get request for review

#### Dropdowns
- `GET /dropdowns/product-lines` - Get product lines
- `GET /dropdowns/plants` - Get plants
- `GET /dropdowns/customers` - Get customers

---

## SMTP Configuration Examples

### Office 365 / Outlook

```env
SMTP_HOST=smtp.office365.com
SMTP_PORT=587
SMTP_USER=your-email@avocarbon.com
SMTP_PASSWORD=your-app-specific-password
SMTP_FROM=notifications@avocarbon.com
```

### Gmail (with app password)

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-specific-password
SMTP_FROM=your-email@gmail.com
```

### Standard SMTP Server

```env
SMTP_HOST=mail.avocarbon.com
SMTP_PORT=25
SMTP_USER=username
SMTP_PASSWORD=password
SMTP_FROM=noreply@avocarbon.com
```

---

## Troubleshooting

### Backend Issues

**Port already in use**
```bash
# Change port:
uvicorn app.main:app --reload --port 5003
```

**Database connection error**
```bash
# Check PostgreSQL is running
# Verify .env DATABASE settings
# Test connection:
psql -h localhost -U postgres -d avocarbon_pricing
```

**Email not sending**
```bash
# Check SMTP settings in .env
# Verify email credentials
# Check firewall/port 587
# Review logs for SMTP errors
```

### Frontend Issues

**Cannot connect to backend**
```bash
# Verify backend is running on port 5002
# Check VITE_BACKEND_URL in frontend .env
# Check browser console for CORS errors
```

**Dropdowns empty**
```bash
# Verify customers.ods or customers.xlsx exists in /data folder
# Check file permissions
# Review backend logs
```

---

## Database Backup

### Backup Database

```bash
pg_dump avocarbon_pricing > backup.sql
```

### Restore Database

```bash
psql avocarbon_pricing < backup.sql
```

---

## Production Deployment

### Before Deployment

1. Set `DEBUG=False` in .env
2. Use strong database password
3. Use strong JWT_SECRET_KEY
4. Configure proper SMTP server
5. Set correct FRONTEND_BASE_URL and BACKEND_BASE_URL
6. Run database migrations
7. Test all three user workflows

### Deploy Backend

```bash
# Using Gunicorn (production ASGI server)
pip install gunicorn

gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:5002 \
  --access-logfile - \
  --error-logfile -
```

### Deploy Frontend

```bash
# Build for production
npm run build

# Output in dist/ folder
# Serve with Nginx or similar
```

---

## Support & Documentation

See `IMPROVEMENTS.md` for detailed technical documentation.

For issues, check logs:
- Backend: Terminal where `uvicorn` is running
- Frontend: Browser console (F12)
- Database: PostgreSQL logs

---

## License

Internal Use Only - AVO Carbon Group
