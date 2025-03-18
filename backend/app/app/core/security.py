from datetime import datetime, timedelta
from typing import Any, Union
from passlib.context import CryptContext
from app.core.config import settings
from jose import jwt
import hashlib

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = "HS256"


"""This file is to imporove the security 
   asspect of the project
   such as : 
           password_hashing,
           user_authentication,
           password verification"""
           
def get_password_hash(password:str):
    return pwd_context.hash(password)

def verify_password(plain_password: str, password: str):
    """
    Verify if the plain password matches the hashed password.
    """

    return pwd_context.verify(plain_password, password)

def check_authcode(authcode: str, auth_text: str):
    """
    Validate the provided authentication code by salting the auth_text.
    """
    salt = settings.SALT_KEY
   
    auth_text = salt+auth_text
    
    result = hashlib.sha1(auth_text.encode())   
    print( result.hexdigest())
    if authcode == result.hexdigest():
        return True
    else:
        return None