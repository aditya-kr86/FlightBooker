from pydantic import BaseModel, EmailStr, ConfigDict, field_validator
from typing import Optional
from datetime import datetime
import re


# ============== Authentication Schemas ==============

class SendOTPRequest(BaseModel):
    """Schema for requesting OTP."""
    email: EmailStr


class VerifyOTPRequest(BaseModel):
    """Schema for verifying OTP."""
    email: EmailStr
    otp: str
    
    @field_validator('otp')
    @classmethod
    def validate_otp(cls, v):
        if not v or len(v) != 6 or not v.isdigit():
            raise ValueError('OTP must be 6 digits')
        return v


class ResetPasswordRequest(BaseModel):
    """Schema for resetting password."""
    email: EmailStr
    otp: str
    new_password: str
    
    @field_validator('otp')
    @classmethod
    def validate_otp(cls, v):
        if not v or len(v) != 6 or not v.isdigit():
            raise ValueError('OTP must be 6 digits')
        return v
    
    @field_validator('new_password')
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        return v


class OTPResponse(BaseModel):
    """Schema for OTP response."""
    success: bool
    message: str


class UserRegister(BaseModel):
    """Schema for user registration (signup)."""
    first_name: str
    last_name: str
    email: EmailStr
    mobile: Optional[str] = None
    country: Optional[str] = None
    password: str
    otp: str  # Required OTP for verification
    
    @field_validator('first_name', 'last_name')
    @classmethod
    def validate_name(cls, v):
        if not v or len(v.strip()) < 2:
            raise ValueError('Name must be at least 2 characters')
        return v.strip().title()
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        return v
    
    @field_validator('mobile')
    @classmethod
    def validate_mobile(cls, v):
        if v:
            # Remove spaces and dashes
            cleaned = re.sub(r'[\s\-]', '', v)
            if not re.match(r'^\+?[\d]{10,15}$', cleaned):
                raise ValueError('Invalid mobile number format')
            return cleaned
        return v
    
    @field_validator('otp')
    @classmethod
    def validate_otp(cls, v):
        if not v or len(v) != 6 or not v.isdigit():
            raise ValueError('OTP must be 6 digits')
        return v


class UserLogin(BaseModel):
    """Schema for user login."""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Schema for token response after login."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds
    user: "UserResponse"


class PasswordChange(BaseModel):
    """Schema for password change."""
    current_password: str
    new_password: str
    
    @field_validator('new_password')
    @classmethod
    def validate_new_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        return v


# ============== User CRUD Schemas ==============

class UserCreate(BaseModel):
    """Schema for admin to create users (with role assignment)."""
    first_name: str
    last_name: str
    email: EmailStr
    password: str
    mobile: Optional[str] = None
    country: Optional[str] = None
    role: Optional[str] = "customer"
    airline_id: Optional[int] = None
    airport_id: Optional[int] = None


class UserUpdate(BaseModel):
    """Schema for updating user profile."""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    mobile: Optional[str] = None
    country: Optional[str] = None
    
    @field_validator('first_name', 'last_name')
    @classmethod
    def validate_name(cls, v):
        if v is not None and len(v.strip()) < 2:
            raise ValueError('Name must be at least 2 characters')
        return v.strip().title() if v else v


class UserAdminUpdate(BaseModel):
    """Schema for admin to update any user field including role."""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    mobile: Optional[str] = None
    country: Optional[str] = None
    role: Optional[str] = None
    airline_id: Optional[int] = None
    airport_id: Optional[int] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None


class UserResponse(BaseModel):
    """Schema for user response."""
    id: int
    first_name: str
    last_name: str
    full_name: str
    email: EmailStr
    mobile: Optional[str] = None
    country: Optional[str] = None
    role: str
    is_active: bool
    is_verified: bool
    created_at: Optional[datetime] = None
    airline_id: Optional[int] = None
    airport_id: Optional[int] = None
    
    model_config = ConfigDict(from_attributes=True)


class UserProfileResponse(BaseModel):
    """Schema for user profile (includes more details)."""
    id: int
    first_name: str
    last_name: str
    full_name: str
    email: EmailStr
    mobile: Optional[str] = None
    country: Optional[str] = None
    role: str
    is_active: bool
    is_verified: bool
    created_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    airline_id: Optional[int] = None
    airport_id: Optional[int] = None
    # Include counts
    total_bookings: Optional[int] = 0
    
    model_config = ConfigDict(from_attributes=True)


# Update forward references
TokenResponse.model_rebuild()

