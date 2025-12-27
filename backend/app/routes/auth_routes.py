"""Authentication routes for login, signup, and token management."""
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.config import get_db
from app.models.user import User
from app.schemas.user_schema import (
    UserRegister,
    UserLogin,
    TokenResponse,
    UserResponse,
    PasswordChange,
    SendOTPRequest,
    VerifyOTPRequest,
    ResetPasswordRequest,
    OTPResponse,
)
from app.auth.password import hash_password, verify_password
from app.auth.jwt_handler import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from app.auth.dependencies import get_current_user
from app.services.email_service import send_registration_otp, send_password_reset_otp, verify_otp, clear_otp, store_otp

router = APIRouter()


@router.post("/send-otp", response_model=OTPResponse)
def send_otp_for_registration(payload: SendOTPRequest, db: Session = Depends(get_db)):
    """
    Send OTP to email for registration verification.
    
    - Checks if email is already registered
    - Generates and sends OTP via email
    """
    # Check if email already exists
    existing = db.query(User).filter(User.email == payload.email.lower()).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Send OTP
    success, message = send_registration_otp(payload.email.lower())
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=message
        )
    
    return OTPResponse(success=True, message="OTP sent to your email. Please check your inbox.")


@router.post("/verify-otp", response_model=OTPResponse)
def verify_registration_otp(payload: VerifyOTPRequest):
    """
    Verify OTP without completing registration.
    
    This allows frontend to verify OTP before submitting full registration form.
    """
    success, message = verify_otp(payload.email.lower(), payload.otp)
    
    # Re-store OTP on successful verification for the actual registration
    if success:
        from app.services.email_service import store_otp
        store_otp(payload.email.lower(), payload.otp)
    
    return OTPResponse(success=success, message=message)


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(payload: UserRegister, db: Session = Depends(get_db)):
    """
    Register a new user account.
    
    - Users register as 'customer' role by default
    - Email must be unique
    - OTP must be verified before registration
    - Password is hashed before storage
    """
    # Verify OTP first
    otp_valid, otp_message = verify_otp(payload.email.lower(), payload.otp)
    if not otp_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=otp_message
        )
    
    # Check if email already exists
    existing = db.query(User).filter(User.email == payload.email.lower()).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    user = User(
        first_name=payload.first_name,
        last_name=payload.last_name,
        email=payload.email.lower(),
        mobile=payload.mobile,
        country=payload.country,
        password_hash=hash_password(payload.password),
        role="customer",  # New users are always customers
        is_active=True,
        is_verified=True,  # Verified via OTP
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user


@router.post("/login", response_model=TokenResponse)
def login_user(payload: UserLogin, db: Session = Depends(get_db)):
    """
    Authenticate user and return JWT token.
    
    - Validates email and password
    - Returns access token on success
    - Updates last_login timestamp
    """
    # Find user by email
    user = db.query(User).filter(User.email == payload.email.lower()).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Verify password
    if not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated. Please contact support."
        )
    
    # Update last login
    user.last_login = datetime.now(timezone.utc)
    db.commit()
    
    # Create access token
    token_data = {
        "sub": str(user.id),
        "email": user.email,
        "role": user.role,
    }
    
    # Add airline/airport ID if staff
    if user.airline_id:
        token_data["airline_id"] = user.airline_id
    if user.airport_id:
        token_data["airport_id"] = user.airport_id
    
    access_token = create_access_token(token_data)
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserResponse(
            id=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
            full_name=user.full_name,
            email=user.email,
            mobile=user.mobile,
            country=user.country,
            role=user.role,
            is_active=user.is_active,
            is_verified=user.is_verified,
            created_at=user.created_at,
            airline_id=user.airline_id,
            airport_id=user.airport_id,
        )
    )


@router.get("/me", response_model=UserResponse)
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """
    Get the current authenticated user's profile.
    """
    return current_user


@router.post("/change-password")
def change_password(
    payload: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Change the current user's password.
    
    - Requires current password verification
    - New password must meet complexity requirements
    """
    # Verify current password
    if not verify_password(payload.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Check new password is different
    if payload.current_password == payload.new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be different from current password"
        )
    
    # Update password
    current_user.password_hash = hash_password(payload.new_password)
    db.commit()
    
    return {"message": "Password changed successfully"}


@router.post("/forgot-password", response_model=OTPResponse)
def forgot_password(payload: SendOTPRequest, db: Session = Depends(get_db)):
    """
    Send OTP to email for password reset.
    
    - Checks if email exists (user must be registered)
    - Generates and sends OTP via email
    """
    # Check if email exists
    user = db.query(User).filter(User.email == payload.email.lower()).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No account found with this email"
        )
    
    # Send OTP for password reset
    success, message = send_password_reset_otp(payload.email.lower())
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=message
        )
    
    return OTPResponse(success=True, message="OTP sent to your email.")


@router.post("/verify-reset-otp", response_model=OTPResponse)
def verify_reset_otp(payload: VerifyOTPRequest):
    """
    Verify OTP for password reset without completing the reset.
    """
    success, message = verify_otp(payload.email.lower(), payload.otp)
    
    # Re-store OTP on successful verification for the actual password reset
    if success:
        store_otp(payload.email.lower(), payload.otp)
    
    return OTPResponse(success=success, message=message)


@router.post("/reset-password", response_model=OTPResponse)
def reset_password(
    payload: ResetPasswordRequest,
    db: Session = Depends(get_db)
):
    """
    Reset password after OTP verification.
    """
    email = payload.email.lower()
    otp = payload.otp
    new_password = payload.new_password
    
    # Verify OTP
    otp_valid, otp_message = verify_otp(email, otp)
    if not otp_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=otp_message
        )
    
    # Find user
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update password
    user.password_hash = hash_password(new_password)
    db.commit()
    
    return OTPResponse(success=True, message="Password reset successfully")


@router.post("/logout")
def logout(current_user: User = Depends(get_current_user)):
    """
    Logout the current user.
    
    Note: With JWT tokens, logout is typically handled client-side by discarding the token.
    This endpoint exists for API completeness and could be extended to implement
    token blacklisting for additional security.
    """
    return {"message": "Logged out successfully"}


@router.post("/refresh-token", response_model=TokenResponse)
def refresh_token(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Refresh the access token for the current user.
    
    - Validates current token
    - Issues a new token with refreshed expiry
    """
    # Create new access token
    token_data = {
        "sub": str(current_user.id),
        "email": current_user.email,
        "role": current_user.role,
    }
    
    if current_user.airline_id:
        token_data["airline_id"] = current_user.airline_id
    if current_user.airport_id:
        token_data["airport_id"] = current_user.airport_id
    
    access_token = create_access_token(token_data)
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserResponse(
            id=current_user.id,
            first_name=current_user.first_name,
            last_name=current_user.last_name,
            full_name=current_user.full_name,
            email=current_user.email,
            mobile=current_user.mobile,
            country=current_user.country,
            role=current_user.role,
            is_active=current_user.is_active,
            is_verified=current_user.is_verified,
            created_at=current_user.created_at,
            airline_id=current_user.airline_id,
            airport_id=current_user.airport_id,
        )
    )
