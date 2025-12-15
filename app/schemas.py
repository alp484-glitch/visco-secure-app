from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional


class UserCreateSchema(BaseModel):
    """User creation input validation"""
    username: str
    email: EmailStr
    password: str

    @field_validator("username")
    def validate_username(cls, v):
        if len(v) < 4 or len(v) > 20:
            raise ValueError("Username length must be between 4 and 20 characters")
        if not v.isalnum():
            raise ValueError("Username can only contain letters and numbers")
        return v

    @field_validator("password")
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not any(char.isdigit() for char in v) or not any(char.isupper() for char in v):
            raise ValueError("Password must contain at least one uppercase letter and one number")
        return v


class ClientDataSchema(BaseModel):
    """Client data input validation"""
    data: str

    @field_validator("data")
    def validate_data(cls, v):
        if len(v) > 1000:
            raise ValueError("Data length cannot exceed 1000 characters")
        return v


class LoginSchema(BaseModel):
    """Login input validation"""
    username: str
    password: str