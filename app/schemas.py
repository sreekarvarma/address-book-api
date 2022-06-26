from pydantic import BaseModel, EmailStr, Field, validator
from typing import List, Union

class HealthCheck(BaseModel):
    status: str = Field('ok', description='Health check status')
    timestamp: int = Field('', description='Timestamp of the health check')

    class Config:
        schema_extra = {
            'example': {
                'status': 'ok',
                'timestamp': 1597490909000
            }
        }

class UserBase(BaseModel):
    name: str = Field(..., example="John Doe", description="User's name")
    email: Union[EmailStr, None] = Field(None, example="john.doe@domain.com", description="User's email")
    phone: str = Field(..., example="555-555-5555", description="User's phone number")
    

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    name: Union[str, None] = Field(None, example="John Doe", description="User's name", min_length=1)
    email: Union[EmailStr, None] = Field(None, example="john.doe@domain.com", description="User's email")
    phone: Union[str, None] = Field(None, example="555-555-5555", description="User's phone number", min_length=1)

class User(UserBase):
    id: int
    address_id: int

    class Config:
        orm_mode = True

class AddressBase(BaseModel):
    door: Union[str, None] = Field(None, example="Apt. 1", description="Address's door")
    street: str = Field(..., example="123 Main St", description="Address's street")
    city: str = Field(..., example="Anytown", description="Address's city")
    state: str = Field(..., example="CA", description="Address's state")
    country: str = Field(..., example="US", description="Address's country")
    zip: str = Field(..., example="12345", description="Address's zip code")
    latitude: float = Field(..., example=37.123, description="Address's latitude")
    longitude: float = Field(..., example=-122.123, description="Address's longitude")

class AddressCreate(AddressBase):
    pass

class AddressUpdate(BaseModel):
    door: Union[str, None] = Field(None, example="Apt. 1", description="Address's door")
    street: Union[str, None] = Field(None, example="123 Main St", description="Address's street",  min_length=1)
    city: Union[str, None] = Field(None, example="Anytown", description="Address's city",  min_length=1)
    state: Union[str, None] = Field(None, example="CA", description="Address's state",  min_length=1)
    country: Union[str, None] = Field(None, example="US", description="Address's country",  min_length=1)
    zip: Union[str, None] = Field(None, example="12345", description="Address's zip code",  min_length=1)
    latitude: Union[float, None] = Field(None, example=37.123, description="Address's latitude")
    longitude: Union[float, None] = Field(None, example=-122.123, description="Address's longitude") 

class Address(AddressBase):
    id: int
    users: List[User] = []

    class Config:
        orm_mode = True

class HttpErrorDetail(BaseModel):
    detail: str

    class Config:
        schema_extra = {
            'example': {
                'detail': 'Bad Request'
            }
        }