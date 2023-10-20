from sqlalchemy import desc, asc
from sqlalchemy.orm import Session

from common.http_exceptions import NOTACCEPTABLE

from . import models
from . import schemas

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    if password is None:
        return None
    return pwd_context.hash(password)

def get_driver(db: Session, driver_id: int):
    return db.query(models.Driver).filter(models.Driver.id == driver_id).first()

def get_driver_by_email(db: Session, email: str):
    return db.query(models.Driver).filter(models.Driver.email == email).first()

def get_driver_by_username(db: Session, username: str):
    return db.query(models.Driver).filter(models.Driver.username == username).first()


def get_drivers(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Driver).offset(skip).limit(limit).all()


def create_driver(db: Session, driver: schemas.DriverCreate):
    hashed_password = get_password_hash(driver.password)
    db_driver = models.Driver(email=driver.email, username=driver.username, hashed_password=hashed_password)
    db.add(db_driver)
    db.commit()
    db.refresh(db_driver)
    return db_driver



def update_driver(db: Session, driver_id: int, driver: schemas.DriverUpdate):
    db_driver = db.query(models.Driver).get(driver_id)

    # Update model class variable from requested fields 
    for var, value in vars(driver).items():
        if value:
            setattr(db_driver, var, value)
    
    if getattr(driver, "password", None):
        if len(driver.password) <= 8: # type: ignore
            raise NOTACCEPTABLE
        hashed_password = get_password_hash(driver.password)
        db_driver.hashed_password = hashed_password # type: ignore
            
    
    db.add(db_driver)
    db.commit()
    # db.refresh(db_driver)
    return db_driver
