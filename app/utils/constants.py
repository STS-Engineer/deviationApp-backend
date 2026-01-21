PRODUCT_LINES = [
    "assembly",
    "friction",
    "injection",
    "seals",
    "brushes",
    "chokes",
]

PLANTS = [
    "Poitiers",
    "Amiens",
    "Mexico",
    "Tianjin",
    "Frankfurt",
    "Tunisia",
    "Kunshan",
    "Chennai",
]

# Status workflow
REQUEST_STATUS_STAGES = {
    "DRAFT": 0,
    "SUBMITTED": 1,
    "UNDER_REVIEW_PL": 2,
    "ESCALATED_TO_VP": 3,
    "APPROVED_BY_PL": 4,
    "APPROVED_BY_VP": 4,
    "REJECTED_BY_PL": 5,
    "REJECTED_BY_VP": 5,
    "BACK_TO_COMMERCIAL": 2,
    "CLOSED": 6,
}
