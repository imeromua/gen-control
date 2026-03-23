import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.common.enums import RoleName


class RoleSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str


class UserBase(BaseModel):
    full_name: str
    username: str


class UserCreate(UserBase):
    password: str
    role_id: uuid.UUID


class UserUpdate(BaseModel):
    full_name: str | None = None
    role_id: uuid.UUID | None = None
    is_active: bool | None = None


class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    role: RoleSchema
    is_active: bool
    created_at: datetime
    updated_at: datetime
