from datetime import datetime
from typing import Generator
from fastapi import  Depends, UploadFile
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import func
from app.db.session import SessionLocal
from sqlalchemy.orm import Session
from app.models import *
from app.core.config import settings
import os

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token")

"""Initializing the database Connection"""
def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

def get_token(token,db:Session=Depends(get_db)):

  token_user=db.query(User).join(Apitoken,Apitoken.user_id==User.user_id).filter(Apitoken.token==token,
                                                                                 Apitoken.status==1,
                                                                                 User.status==1).first()
  return token_user

def mobile_number_verify(phone_number):
    if len(phone_number) !=10:
        return False
    return True 

LOCAL_STORAGE_PATH = "C:/Users/tharu/Desktop/project_ecommerces/backend/app/app/images" 
def save_images(images: list[UploadFile], product_id: int) -> list[str]:
   
    os.makedirs(LOCAL_STORAGE_PATH, exist_ok=True)
    
    stored_image_paths = []

    for image in images:
        file = image.filename.split('.')[-1] 
        filename = f"{product_id}_{image.filename}_{str(datetime.timestamp(datetime.now()))}.{file}"
        file_path = os.path.join(LOCAL_STORAGE_PATH, filename)        
        with open(file_path, "wb") as file:
            file.write(image.file.read())  
        stored_image_paths.append(file_path)

    return stored_image_paths

def calculate_total_amount(db: Session, order_id: int):
    total_amount = (
        db.query(func.sum(OrderDetails.order_price))
        .filter(  OrderDetails.order_id == order_id,  OrderDetails.status == 1)
        .group_by( OrderDetails.order_id )
        .scalar()
    )
    return total_amount 

