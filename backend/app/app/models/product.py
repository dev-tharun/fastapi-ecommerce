from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Text,func,Float
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import TINYINT
from app.db.base_class import Base

class Product(Base):
    __tablename__ = "product"

    product_id = Column(Integer, primary_key=True, autoincrement=True)
    brand_id = Column(Integer, ForeignKey("brand.brand_id"))
    sub_category_id = Column(Integer, ForeignKey("sub_category.sub_category_id"))
    category_product_id = Column(Integer, ForeignKey("category_product.category_product_id")) 
    product_name = Column(String(255))
    product_stock = Column(Integer)
    product_price = Column(Float)
    product_discount = Column(Float)
    discount_product_price = Column(Float)
    product_description = Column(Text)
    status = Column(TINYINT)
    created_at = Column(DateTime, default=func.current_timestamp())

  
    cart = relationship("Cart", back_populates="product")
    wishlist = relationship("Wishlist", back_populates="product")
    sub_category = relationship("SubCategory", back_populates="product")
    category_product = relationship("CategoryProduct", back_populates="product")
    order_details = relationship('OrderDetails', back_populates='product')
    brand = relationship("Brand", back_populates="product")
    productimage=relationship("ProductImage",back_populates="product")