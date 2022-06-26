from fastapi import HTTPException
from sqlalchemy.orm import Session

from . import models, schemas
from haversine import haversine

# address read operations
def get_address(db: Session, address_id: int):
    return db.query(models.Address).filter(models.Address.id == address_id).first()

def get_address_by_coordinates(db: Session, latitude: float, longitude: float):
    return db.query(models.Address).filter(models.Address.latitude == latitude, models.Address.longitude == longitude).first()

def get_addresses(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Address).offset(skip).limit(limit).all()

def get_address_in_range(db: Session, lat: float, lng: float, radius: float):
    given_location = (lat, lng)

    haversine_distance = lambda add_lat, add_lng: haversine(given_location, ((add_lat), (add_lng)))
    addresses = filter(lambda address: haversine_distance(address.latitude, address.longitude) < radius, db.query(models.Address).all())
    return list(addresses)

# address write and update operations
def create_address(db: Session, address: schemas.AddressCreate):
    db_address = models.Address(**address.dict())
    db.add(db_address)
    db.commit()
    db.refresh(db_address)
    return db_address

def delete_address(db: Session, address_id: int):
    db_address = db.query(models.Address).filter(models.Address.id == address_id).first()
    if db_address is None:
        raise HTTPException(status_code=404, detail="Address not found")
    db.delete(db_address)
    db.commit()
    return db_address

def update_address(db: Session, address_id: int, address: schemas.AddressUpdate):
    db_address = db.query(models.Address).filter(models.Address.id == address_id)
    new_db_address = schemas.AddressUpdate()
    db_address_ob = db_address.first()
    # check if address is exist
    if db_address_ob is None:
        raise HTTPException(status_code=404, detail="Address not found")
    # check if any of the fields is provided
    if all(value == None for value in address.dict().values()):
        raise HTTPException(status_code=400, detail="No values to update")
    
    new_db_address.door = address.door if address.door or address.door == '' else None
    new_db_address.street = address.street if address.street else None
    new_db_address.city = address.city if address.city else None
    new_db_address.state = address.state if address.state else None
    new_db_address.country = address.country if address.country else None
    new_db_address.zip = address.zip if address.zip else None

    # check if new location already exists
    if address.latitude or address.longitude:
        if address.latitude == db_address_ob.latitude and address.longitude == db_address_ob.longitude:
            raise HTTPException(status_code=400, detail="Latitude and longitude are not changed")
        if address.latitude:
            new_db_address.latitude = address.latitude
        if address.longitude:
            new_db_address.longitude = address.longitude
        updated_latitude = new_db_address.latitude if new_db_address.latitude else db_address_ob.latitude
        updated_longitude = new_db_address.longitude if new_db_address.longitude else db_address_ob.longitude
        address_coords_match = db.query(models.Address).filter(models.Address.latitude == updated_latitude, models.Address.longitude == updated_longitude).first()
        if address_coords_match:
            raise HTTPException(status_code=400, detail="Updated coordinates matches with the coordinates of another address")
    
    # exclude all the none and empty values so that we don't update this values to none
    new_db_address_data = new_db_address.dict(exclude_none=True, exclude_unset=True)
    
    # update the data with new values
    for key, value in new_db_address_data.items():
        setattr(db_address_ob, key, value)
    
    db.add(db_address_ob)
    db.commit()
    db.refresh(db_address_ob)
    return db_address_ob

# user read operations
def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def get_users_by_address_id(db: Session, address_id: int):
    return db.query(models.User).filter(models.User.address_id == address_id).all()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

# user write and update operations
def create_Address_user(db: Session, address_id: int, user: schemas.UserCreate):
    db_user = models.User(address_id=address_id, **user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_address_user(db: Session, address_id: int, user_id: int):
    db_address = db.query(models.Address).filter(models.Address.id == address_id).first()
    if db_address is None:
        raise HTTPException(status_code=404, detail="Address not found")
    db_user = db.query(models.User).filter(models.User.id == user_id, models.User.address_id == address_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(db_user)
    db.commit()
    return db_user

def update_user(db: Session, user_id: int, user: schemas.UserUpdate):
    db_user = db.query(models.User).filter(models.User.id == user_id)
    new_db_user = schemas.UserUpdate()
    db_user_ob = db_user.first()
    
    # check if user is exist
    if db_user_ob is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    # check if any of the fields is provided
    if all(value == None for value in user.dict().values()):
        raise HTTPException(status_code=400, detail="No values to update")
    new_db_user.name = user.name if user.name else None
    new_db_user.phone = user.phone if user.phone else None
    
    # check if email is new
    if user.email:
        if user.email == db_user_ob.email:
            raise HTTPException(status_code=400, detail="Email is not changed")
        user_with_email = db.query(models.User).filter(models.User.email == user.email).first()
        if user_with_email:
            raise HTTPException(status_code=400, detail="Email is been used by another user")
        new_db_user.email = user.email
    
    # remove all the none and unset values so that we don't update this values to none
    new_db_user_data = new_db_user.dict(exclude_unset=True, exclude_none=True)
    
    # update the data with new values
    for key, value in new_db_user_data.items():
        setattr(db_user_ob, key, value)
    
    db.add(db_user_ob)
    db.commit()
    db.refresh(db_user_ob)
    return db_user_ob
    