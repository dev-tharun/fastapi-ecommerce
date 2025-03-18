from sqlalchemy import  DECIMAL, Column, Date, ForeignKey, Integer, String, DateTime,func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import TINYINT
from app.db.base_class import Base

class Bill(Base):
    __tablename__ = 'bill'

    bill_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('user.user_id'))
    order_id = Column(Integer, ForeignKey('order.order_id'))
    payment_method= Column(String(200))
    bill_address = Column(String(255), nullable=True) 
    total_amount = Column(DECIMAL(10, 2),nullable=True)
    date = Column(Date)  
    status = Column(TINYINT) 
    created_at = Column(DateTime, default=func.current_timestamp())
   
    user = relationship("User", back_populates="bill")
    order = relationship("Order", back_populates="bill")
    