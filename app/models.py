from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .database import Base

class Address(Base):
    __tablename__ = "address"
    id = Column(Integer, primary_key=True, index=True)
    door = Column(String(50), nullable=True)
    street = Column(String, nullable=False)
    city = Column(String, nullable=False)
    state = Column(String, nullable=False)
    country = Column(String, nullable=False)
    zip = Column(String, nullable=False)
    latitude = Column(Integer, nullable=False)
    longitude = Column(Integer, nullable=False)

    users = relationship("User", back_populates="address")

    def __repr__(self):
        return f"<Address(id={self.id}, door={self.door}, street={self.street}, city={self.city}, state={self.state}, country={self.country} zip={self.zip}, latitude={self.latitude}, longitude={self.longitude})>"

class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=False)
    address_id = Column(Integer, ForeignKey("address.id"), nullable=False)

    address = relationship("Address", back_populates="users")

    def __repr__(self):
        return f"<User(id={self.id}, name={self.name}, email={self.email}, address_id={self.address_id})"