from sqlalchemy import  Column, Integer, String, DateTime, Text,func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import TINYINT
from app.db.base_class import Base

class Brand(Base):
    __tablename__ = "brand"
    brand_id=Column(Integer, primary_key=True, autoincrement=True)
    brand_name=Column(String(255))
    brand_description=Column(Text)
    status = Column(TINYINT)  
    created_at = Column(DateTime, default=func.current_timestamp())

    product = relationship("Product", back_populates="brand")