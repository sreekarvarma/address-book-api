import time
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from typing import List

import logging

from . import crud, models, schemas
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

logging.basicConfig()
logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)
logging.getLogger("sqlalchemy.pool").setLevel(logging.DEBUG)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get('/', response_model=schemas.HealthCheck)
def health_check():
    return {
        "status": "ok",
        "timestamp": int(time.time()*1000)
    }

@app.post("/addresses/", response_model=schemas.Address, responses={400: {"model": schemas.HttpErrorDetail}})
def create_address(address: schemas.AddressCreate, db: Session = Depends(get_db)):
    db_address = crud.get_address_by_coordinates(db, address.latitude, address.longitude)
    if db_address:
        raise HTTPException(status_code=400, detail="Address with given coordinates already exists")
    return crud.create_address(db=db, address=address)

@app.get("/addresses/", response_model=List[schemas.Address])
def read_addresses(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_addresses(db=db, skip=skip, limit=limit)

@app.get("/addresses/within_range/")
def read_addresses_in_range(latitude: float, longitude: float, radius: float, db: Session = Depends(get_db)):
    return crud.get_address_in_range(db=db, lat=latitude, lng=longitude, radius=radius)

@app.get("/addresses/{address_id}", response_model=schemas.Address)
def read_address(address_id: int, db: Session = Depends(get_db)):
    db_address = crud.get_address(db=db, address_id=address_id)
    if db_address is None:
        raise HTTPException(status_code=404, detail="Address not found")
    return db_address

@app.post("/addresses/{address_id}/users/", response_model=schemas.User)
def create_user_for_address(address_id: int, user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_address = crud.get_address(db=db, address_id=address_id)
    if db_address is None:
        raise HTTPException(status_code=404, detail="Address not found")
    db_user = crud.get_user_by_email(db=db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="User with given email already exists")
    return crud.create_Address_user(db=db, address_id=address_id, user=user)

@app.get("/addresses/{address_id}/users/", response_model=List[schemas.User], responses={404: {"model": schemas.HttpErrorDetail}})
def read_users_for_address(address_id: int, db: Session = Depends(get_db)):
    db_address = crud.get_address(db=db, address_id=address_id)
    if db_address is None:
        raise HTTPException(status_code=404, detail="Address not found")
    return crud.get_users_by_address_id(db=db, address_id=address_id)

@app.delete("/addresses/{address_id}/users/{user_id}", response_model=schemas.User ,responses={404: {"model": schemas.HttpErrorDetail}})
def delete_user_for_address(address_id: int, user_id: int, db: Session = Depends(get_db)):
    return crud.delete_address_user(db=db, address_id=address_id, user_id=user_id)

@app.delete("/addresses/{address_id}", response_model=schemas.Address, responses={404: {"model": schemas.HttpErrorDetail}})
def delete_address(address_id: int, db: Session = Depends(get_db)):
    return crud.delete_address(db=db, address_id=address_id)

@app.patch("/addresses/{address_id}", response_model=schemas.Address, responses={404: {"model": schemas.HttpErrorDetail}, 400: {"model": schemas.HttpErrorDetail}})
def update_address(address_id: int, address: schemas.AddressUpdate, db: Session = Depends(get_db)):
    return crud.update_address(db=db, address_id=address_id, address=address)

@app.patch("/users/{user_id}", response_model=schemas.User, responses={404: {"model": schemas.HttpErrorDetail}, 400: {"model": schemas.HttpErrorDetail}})
def update_user(user_id: int, user: schemas.UserUpdate, db: Session = Depends(get_db)):
    return crud.update_user(db=db, user_id=user_id, user=user)
