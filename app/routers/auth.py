import random
import string
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from app.emails.mailer import send_verification_email
from app.utils.users import get_users_by_role

router = APIRouter(prefix="/auth", tags=["Auth"])

# In-memory storage for verification codes (email -> {code, role, expires_at})
verification_codes = {}


class SendVerificationRequest(BaseModel):
    email: EmailStr
    role: str = "COMMERCIAL"


class VerifyCodeRequest(BaseModel):
    email: EmailStr
    code: str
    role: str


class UserInfo(BaseModel):
    email: str
    role: str
    token: str


class UserLogin(BaseModel):
    email: EmailStr
    role: str = "COMMERCIAL"  # Allow user to select role during login


class UserOption(BaseModel):
    name: str
    email: str


def generate_verification_code():
    """Generate a 6-digit verification code"""
    return ''.join(random.choices(string.digits, k=6))

@router.post("/send-verification-code")
async def send_verification_code(request: SendVerificationRequest):
    """
    Send verification code to email address.
    """
    email = request.email.lower()
    role = request.role.upper()

    # Validate role
    valid_roles = ["COMMERCIAL", "PL", "VP"]
    if role not in valid_roles:
        role = "COMMERCIAL"

    # Generate verification code
    code = generate_verification_code()
    expires_at = datetime.utcnow() + timedelta(minutes=10)  # Code valid for 10 minutes

    # Store verification code
    verification_codes[email] = {
        "code": code,
        "role": role,
        "expires_at": expires_at
    }

    # Send email with verification code
    try:
        await send_verification_email(email, code)
    except Exception as e:
        # If email fails, still return success but log the error
        print(f"Failed to send verification email to {email}: {e}")
        # For testing, you could comment this to allow proceeding without email

    return {
        "message": "Verification code sent to email",
        "email": email,
        "role": role
    }


@router.post("/verify-code")
def verify_code(request: VerifyCodeRequest) -> UserInfo:
    """
    Verify the code sent to email and return user info with token.
    """
    email = request.email.lower()
    code = request.code.strip()
    role = request.role.upper()

    # Check if verification code exists
    if email not in verification_codes:
        raise HTTPException(status_code=400, detail="No verification code sent to this email")

    stored_data = verification_codes[email]

    # Check if code has expired
    if datetime.utcnow() > stored_data["expires_at"]:
        del verification_codes[email]
        raise HTTPException(status_code=400, detail="Verification code has expired. Please request a new one.")

    # Check if code matches
    if code != stored_data["code"]:
        raise HTTPException(status_code=400, detail="Invalid verification code")

    # Check if role matches
    if role != stored_data["role"]:
        raise HTTPException(status_code=400, detail="Role mismatch")

    # Code is valid, create token (simple token: email:role:timestamp)
    token = f"{email}:{role}:{datetime.utcnow().isoformat()}"

    # Clean up used verification code
    del verification_codes[email]

    return UserInfo(email=email, role=role, token=token)


@router.get("/users/{role}", response_model=list[UserOption])
def get_users_for_role(role: str):
    """
    Get list of users for a specific role
    """
    users = get_users_by_role(role)
    return users


@router.post("/login")
def login(user: UserLogin) -> UserInfo:
    """
    Email-based login with user-selected role.
    Users can choose their role during login (COMMERCIAL, PL, or VP).
    """
    email = user.email.lower()
    role = user.role.upper()

    # Validate role
    valid_roles = ["COMMERCIAL", "PL", "VP"]
    if role not in valid_roles:
        role = "COMMERCIAL"  # Default to COMMERCIAL if invalid

    # Create token (simple token: email:role:timestamp)
    token = f"{email}:{role}:{datetime.utcnow().isoformat()}"

    return UserInfo(email=email, role=role, token=token)

