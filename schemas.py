from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List


# User Schemas
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str
    username: str


# Vehicle Schemas
class VehicleCreate(BaseModel):
    name: str
    price: float
    year: int
    mileage: float
    color: str
    description: Optional[str] = ""


class VehicleUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    year: Optional[int] = None
    mileage: Optional[float] = None
    color: Optional[str] = None
    description: Optional[str] = None


class VehicleResponse(BaseModel):
    id: int
    name: str
    price: float
    year: int
    mileage: float
    color: str
    description: Optional[str]
    owner_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class VehicleWithOwner(VehicleResponse):
    owner: UserResponse


class UserWithVehicles(UserResponse):
    vehicles: List[VehicleResponse]
