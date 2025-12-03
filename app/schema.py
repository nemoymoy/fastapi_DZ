from pydantic import BaseModel, constr, condecimal
import datetime
import uuid
from typing import Literal, Optional

class IdResponseBase(BaseModel):
    id: int

class StatusResponse(BaseModel):
    status: Literal["success"]

class CreateAdvertisementRequest(BaseModel):
    title: constr(min_length=2, max_length=100)
    description: constr(min_length=10, max_length=500)
    price: condecimal(gt=0, max_digits=12, decimal_places=2)

class CreateAdvertisementResponse(IdResponseBase):
    pass

class GetAdvertisementResponse(BaseModel):
    id: int
    title: str
    description: str
    price: int
    created_at: datetime.datetime
    author_id: int

class SearchAdvertisementResponse(BaseModel):
    results: list[GetAdvertisementResponse]

class UpdateAdvertisementRequest(BaseModel):
    title: constr(min_length=2, max_length=100) | None = None
    description: constr(min_length=10, max_length=500) | None = None
    price: condecimal(gt=0, max_digits=12, decimal_places=2) | None = None

class UpdateAdvertisementResponse(StatusResponse):
    pass

class DeleteAdvertisementResponse(StatusResponse):
    pass

class BasicUserRequest(BaseModel):
    name: constr(min_length=2, max_length=100)
    password: constr(min_length=8, max_length=100)
    role: Optional[str] = "user"

class LoginRequest(BasicUserRequest):
    pass

class LoginResponse(BaseModel):
    token: uuid.UUID

class CreateUserRequest(BasicUserRequest):
    pass

class CreateUserResponse(IdResponseBase):
    pass

class GetUserResponse(BaseModel):
    id: int
    name: str
    registration_time: datetime.datetime

class UpdateUserRequest(CreateUserRequest):
    pass

class UpdateUserResponse(StatusResponse):
    pass

class DeleteUserResponse(StatusResponse):
    pass
