from sqlalchemy import  Column, Integer, String, DateTime, Text,func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import TINYINT
from app.db.base_class import Base

class CategoryProduct(Base):   
    __tablename__ = "category_product"  

    category_product_id = Column(Integer, primary_key=True, autoincrement=True)  
    category_product_name = Column(String(255))
    category_product_description = Column(Text(255))
    status = Column(TINYINT)  
    created_at = Column(DateTime, default=func.current_timestamp())


    sub_category = relationship("SubCategory", back_populates="category_product")
    product = relationship("Product", back_populates="category_product")
    