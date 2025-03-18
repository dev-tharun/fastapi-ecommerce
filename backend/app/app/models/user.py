from sqlalchemy import  Column, Integer, String, DateTime,func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import TINYINT
from app.db.base_class import Base

class User(Base):
    __tablename__ = "user"

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    first_name=Column(String(100))
    last_name=Column(String(100))
    user_type=Column(TINYINT)
    email = Column(String(255), unique=True)
    phone_number = Column(String(15),unique=True)
    username = Column(String(100), unique=True)
    password = Column(String(255))
    status = Column(TINYINT,comment=" 1 for Active, 0 for Inactive ")    
    verification=Column(TINYINT,default=0,comment= "0->not verified 1-verified") 
    created_at = Column(DateTime, default=func.now())
 
 
    order = relationship("Order", back_populates="user")  
    cart = relationship("Cart", back_populates="user")
    wishlist = relationship("Wishlist", back_populates="user")
    bill = relationship("Bill", back_populates="user")
    api_token=relationship("Apitoken",back_populates="user")