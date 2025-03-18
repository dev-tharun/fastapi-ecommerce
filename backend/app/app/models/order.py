from sqlalchemy import  Column, Date, ForeignKey, Integer, String, DateTime,func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import TINYINT
from app.db.base_class import Base

class Order(Base):
    __tablename__ = "order"
    order_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.user_id"))
    user_address = Column(String(255))
    city = Column(String(255))
    pincode = Column(String(10))
    order_date = Column(Date)
    pdf_url= Column(String(255))
    delivered_at = Column(DateTime)  
    status = Column(TINYINT,comment="1-active 0-inactive")
    created_at = Column(DateTime, default=func.current_timestamp())


    user = relationship("User", back_populates="order")  
    order_details = relationship('OrderDetails', back_populates="order")
    bill = relationship("Bill", back_populates="order")
   

  