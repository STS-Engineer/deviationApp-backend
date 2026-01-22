# Avocarbon Pricing Deviation Workflow

## Visual Workflow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         COMMERCIAL PHASE                                    │
│                                                                             │
│  1. Commercial user fills pricing deviation form                           │
│     - Costing number, project name, customer                              │
│     - Product line, plant, sales info                                     │
│     - Initial price vs Target price (negotiated)                          │
│     - Problem/reason for deviation                                        │
│     - PL responsible contact                                              │
│                                                                             │
│  2. Form submitted to system                                               │
│     - System validates all fields                                          │
│     - Checks costing number is unique                                      │
│     - Verifies target < initial price                                      │
│                                                                             │
│  3. Automatic email sent to PL Responsible                                 │
│     - Request details included                                             │
│     - Direct link to review portal                                         │
│                                                                             │
│  Status: UNDER_REVIEW_PL                                                   │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    PRODUCT LINE RESPONSIBLE PHASE                           │
│                                                                             │
│  1. PL Responsible receives email                                          │
│                                                                             │
│  2. Reviews the pricing deviation request                                  │
│     - Can see all request details                                          │
│     - Price difference calculated                                          │
│     - Reason for deviation explained                                       │
│                                                                             │
│  3. PL Makes Decision:                                                     │
│                                                                             │
│     ┌─────────────────────────────────────────────────────────────────┐   │
│     │ OPTION 1: APPROVE                                              │   │
│     ├─────────────────────────────────────────────────────────────────┤   │
│     │ - Accept the negotiated price                                  │   │
│     │ - Status → APPROVED_BY_PL                                      │   │
│     │ - Email sent to Commercial: Decision = APPROVED                │   │
│     │ - Commercial can now close the deal                            │   │
│     └─────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│     ┌─────────────────────────────────────────────────────────────────┐   │
│     │ OPTION 2: SUGGEST ALTERNATIVE PRICE                            │   │
│     ├─────────────────────────────────────────────────────────────────┤   │
│     │ - Suggest middle ground price (between initial & target)       │   │
│     │ - Add professional comments/reasoning                          │   │
│     │ - Status → APPROVED_BY_PL                                      │   │
│     │ - Email sent to Commercial with suggested price                │   │
│     │ - Commercial can accept or renegotiate                         │   │
│     └─────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│     ┌─────────────────────────────────────────────────────────────────┐   │
│     │ OPTION 3: REJECT                                               │   │
│     ├─────────────────────────────────────────────────────────────────┤   │
│     │ - Reject the price deviation                                   │   │
│     │ - Must provide detailed comments/reasoning                     │   │
│     │ - Status → BACK_TO_COMMERCIAL                                  │   │
│     │ - Email sent to Commercial: Decision = REJECTED                │   │
│     │ - Commercial can adjust price or close                         │   │
│     └─────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│     ┌─────────────────────────────────────────────────────────────────┐   │
│     │ OPTION 4: ESCALATE TO VP                                       │   │
│     ├─────────────────────────────────────────────────────────────────┤   │
│     │ - Need VP approval (significant deviation)                     │   │
│     │ - Can suggest alternative price                                │   │
│     │ - Must provide detailed business justification                 │   │
│     │ - Status → ESCALATED_TO_VP                                     │   │
│     │ - Email sent to VP with full context                           │   │
│     └─────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                         ┌────────────┼────────────┐
                         │            │            │
                    APPROVED      REJECTED     ESCALATED
                         │            │            │
                         ▼            ▼            ▼
                      ┌──────┐  ┌──────────┐  ┌───────────┐
                      │EMAIL │  │BACK TO   │  │    VP     │
                      │COMM  │  │COMM      │  │  PHASE    │
                      └──────┘  └──────────┘  └───────────┘
                         │            │            │
                         └────────────┴────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         VP REVIEW PHASE (if escalated)                      │
│                                                                             │
│  1. VP receives escalation email                                           │
│     - Request details                                                       │
│     - PL's justification for escalation                                    │
│     - Price comparison                                                      │
│                                                                             │
│  2. VP Reviews the request                                                 │
│     - Strategic importance                                                  │
│     - Business impact                                                       │
│     - Customer relationship value                                          │
│                                                                             │
│  3. VP Makes Final Decision:                                               │
│                                                                             │
│     ┌─────────────────────────────────────────────────────────────────┐   │
│     │ OPTION 1: APPROVE                                              │   │
│     ├─────────────────────────────────────────────────────────────────┤   │
│     │ - Accept the negotiated price                                  │   │
│     │ - Status → CLOSED                                              │   │
│     │ - Email sent to Commercial: FINAL APPROVAL                     │   │
│     │ - Deal is closed                                               │   │
│     └─────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│     ┌─────────────────────────────────────────────────────────────────┐   │
│     │ OPTION 2: SUGGEST ALTERNATIVE PRICE & APPROVE                  │   │
│     ├─────────────────────────────────────────────────────────────────┤   │
│     │ - Set final approved price                                     │   │
│     │ - Status → CLOSED                                              │   │
│     │ - Email to Commercial with final price                         │   │
│     └─────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│     ┌─────────────────────────────────────────────────────────────────┐   │
│     │ OPTION 3: REJECT                                               │   │
│     ├─────────────────────────────────────────────────────────────────┤   │
│     │ - Reject the price deviation                                   │   │
│     │ - Must provide VP-level justification                          │   │
│     │ - Status → BACK_TO_COMMERCIAL                                  │   │
│     │ - Email to Commercial: FINAL REJECTION                         │   │
│     │ - Commercial can adjust or abandon deal                        │   │
│     └─────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                         ┌────────────┼────────────┐
                         │            │            │
                    APPROVED      REJECTED      CLOSED
                         │            │            │
                         └────────────┴────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      COMMERCIAL CLOSE PHASE                                 │
│                                                                             │
│  1. Commercial receives final decision email                               │
│                                                                             │
│  2. If APPROVED:                                                           │
│     - Can proceed with customer at approved price                          │
│     - Mark request as closed                                               │
│     - Proceed with order                                                    │
│                                                                             │
│  3. If REJECTED:                                                           │
│     - Can renegotiate price with customer                                  │
│     - Resubmit request with new price                                      │
│     - OR close deal at original price                                       │
│     - OR walk away from customer                                            │
│                                                                             │
│  Final Status: CLOSED                                                       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Status Flow Diagram

```
                          START
                            │
                            ▼
                    ┌───────────────────┐
                    │ Commercial Creates│
                    │ and Submits       │
                    └─────────┬─────────┘
                              │
                              ▼
                    ┌─────────────────────┐
                    │ UNDER_REVIEW_PL     │
                    │ (PL is reviewing)   │
                    └────┬────────┬────┬──┘
                         │        │    │
           ┌─────────────┘        │    └──────────────┐
           │                      │                   │
           ▼                      ▼                   ▼
    ┌────────────────┐   ┌──────────────┐   ┌──────────────┐
    │ APPROVED_BY_PL │   │BACK_TO_COMM  │   │ESCALATED_TO_ │
    │ (PL Approved)  │   │(PL Rejected) │   │ VP(Needs VP) │
    └────────┬───────┘   └──────┬───────┘   └──────┬───────┘
             │                  │                   │
             │       ┌──────────┘                   │
             │       │                              │
             ▼       ▼                              ▼
        ┌─────────────────────┐         ┌───────────────────────┐
        │ Email to Commercial │         │ VP Reviews Request    │
        │ Decision Sent       │         │ (ESCALATED_TO_VP)     │
        └─────────┬───────────┘         └────┬───────┬─────┬───┘
                  │                          │       │     │
                  │             ┌────────────┘       │     └──────────┐
                  │             │                    │                │
                  │             ▼                    ▼                ▼
                  │      ┌──────────────┐   ┌──────────────┐   ┌────────────┐
                  │      │APPROVED_BY_VP│   │BACK_TO_COMM  │   │  CLOSED    │
                  │      │(VP Approved) │   │(VP Rejected) │   │(Approved)  │
                  │      └──────┬───────┘   └──────┬───────┘   └────┬───────┘
                  │             │                  │                │
                  └─────┬───────┴──────────────────┘                │
                        │                                          │
                        │    ┌──────────────────────────────────┬──┘
                        │    │                                  │
                        ▼    ▼                                  ▼
                    ┌──────────────────┐              ┌──────────────────┐
                    │ Commercial Can:  │              │   CLOSED STATUS  │
                    │ - Accept/Close   │              │ - Deal Done      │
                    │ - Renegotiate    │              │ - Request Closed │
                    │ - Abandon        │              │ - Archive Info   │
                    └────────┬─────────┘              └──────────────────┘
                             │
                             ▼
                        ┌─────────────┐
                        │   END       │
                        └─────────────┘
```

---

## Email Communication Flow

```
┌─────────────┐
│  Commercial │
└──────┬──────┘
       │ Submits Request
       ▼
    [Email] ──► PL Responsible: "Please Review This Request"
       │        - Request details
       │        - Price info
       │        - Action link
       │
       ├─────────────────────────────────────────────┐
       │                                             │
       ▼ (PL Reviews & Decides)                     ▼ (PL Reviews & Decides)
    [Email] ◄── PL to Commercial                [Email] ◄── PL to Commercial
    "APPROVED"                                   "REJECTED" or "SUGGEST PRICE"
       │                                             │
       ├──────────────────────┬─────────────────────┤
       │                      │                     │
       ▼ (If Escalate)        ▼                    ▼
    [Email] ──► VP: "Escalation for Review"     Commercial Decides Next Step
       │        - Full details
       │        - PL reasoning
       │
       ├─────────────────────┬─────────────────┐
       │                     │                 │
       ▼                     ▼                 ▼
    [Email] ◄──         [Email] ◄──       [Email] ◄──
    "APPROVED"          "REJECTED"        "SUGGEST PRICE"
       │                 │                 │
       │                 │                 │
       └────────┬────────┴────────┬────────┘
                │                 │
                ▼                 ▼
          Commercial        Commercial
          Closes Deal    Renegotiates/Abandons
```

---

## Data Storage Structure

```
PRICING_REQUEST Table
├── Primary Info
│   ├── id (primary key)
│   ├── costing_number (unique)
│   ├── project_name
│   └── customer
│
├── Request Details
│   ├── product_line
│   ├── plant
│   ├── yearly_sales
│   ├── initial_price
│   ├── target_price
│   ├── problem_to_solve
│   └── attachment_path
│
├── Requester Info
│   ├── requester_email
│   ├── requester_name
│   ├── product_line_responsible_email
│   ├── product_line_responsible_name
│   ├── vp_email
│   └── vp_name
│
├── PL Decision Info
│   ├── pl_suggested_price
│   ├── pl_comments
│   └── pl_decision_date
│
├── VP Decision Info
│   ├── vp_suggested_price
│   ├── vp_comments
│   └── vp_decision_date
│
├── Final Info
│   ├── final_approved_price
│   └── status
│
└── Timestamps
    ├── created_at
    └── updated_at
```

---

## Key Metrics & Tracking

### Tracked in System:
- Request creation date/time
- PL decision date/time
- VP decision date/time
- Turnaround time per stage
- Approval rate by PL/VP
- Average price deviation percentage
- Customer negotiation success rate

### Available for Reporting:
- Requests by product line
- Requests by plant
- Requests by customer
- Approval/rejection rates
- Time in each stage
- Final price variance

---

## Security & Audit

### Email Validation:
- All users must have @avocarbon.com email

### Audit Trail:
- All decisions logged with timestamps
- Comments stored for history
- Status changes tracked
- Decision makers identified

### Access Control:
- Commercial: Can only see their own requests
- PL: Can see requests for their product line
- VP: Can see escalated requests
- Admin: Can see all requests

