from fastapi import APIRouter, Depends, Form
from sqlalchemy.orm import Session
from app.models import *
from app.api import deps
from app.core.security import get_password_hash, verify_password
from app.utils import *
import random

router = APIRouter()

@router.post("/signup-user")
async def signup_user(db:Session=Depends(deps.get_db),
                      user_name:str=Form(...),
                      first_name:str=Form(...),
                      last_name:str=Form(None),
                      user_type:int=Form(...,description="1-user 2-admin"),
                      email:str=Form(...),
                      phone_number:str=Form(None),
                      pasword:str=Form(...)):
    
    get_user = db.query(User).filter(User.status ==1)
    
    check_user_name = get_user.filter(User.username == user_name).first()
    if check_user_name:
        return {"status":0,"msg":"User name already exits."}
    
    check_email =  get_user.filter(User.email == email).first()
    if check_email:
        return {"status":0,"msg":"Email already exits."}
    

    phone_number = deps.mobile_number_verify(phone_number)
    if not phone_number:
        return {"status":0,"msg":"please fill the 10 digit mobile number"}
    check_phone_number =  get_user.filter(User.phone_number == phone_number).first()
    if check_phone_number:
        return {"status":0,"msg":"Mobile number already exits."}
    
    create_user = User(
        username=user_name,
        first_name=first_name,
        last_name=last_name,
        email=email,
        phone_number=phone_number,
        user_type=user_type,
        password =get_password_hash(pasword), 
        verification=0,
        status=1 
        )
    db.add(create_user)
    db.commit()

    
    char1 = 'qwertyuioplkjhgfdsazxcvbnm1234567890'
    char2 = 'QWERTYUIOPLKJHGFDSAZXCVBNM0123456789'
    reset_character = char1 + char2
    key = ''.join(random.choices(reset_character, k=20))
        
    token =f"{key}nTew45@!"
    
    create_token = Apitoken(
            user_id = create_user.user_id,
            token = token,
            status = 1
        )
    db.add(create_token)
    db.commit()

    return {"status":1,"msg":"Signup successfully","token":token}
     
@router.post("/verify-otp")
async def verify_otp(
    token: str=Form(...),
    otp: str=Form(...),
    db: Session = Depends(deps.get_db)):

    entry_otp="1234"
    user=deps.get_token(token,db)
    if not user:
        return {"status":0,"msg":"no user found"}
    temporary_token_delete=db.query(Apitoken).filter(Apitoken.user_id == user.user_id,Apitoken.status == 1).first()
    
    if otp  ==  entry_otp:
        user.verification = 1
        temporary_token_delete.status = -1
        db.commit()
        return {"status": 1,"msg":"Email successfully verified"}
    else:
        return {"status": 0, "msg":"Invalid OTP"}
    
@router.post('/login-user')
async def login_user(db: Session = Depends(deps.get_db),
                    user_name: str = Form(...),
                    password: str = Form(...)):
    
    checkUser = db.query(User).filter(User.username == user_name,User.status == 1).first()
    
    if not checkUser:
        return {"status":0,"msg":"User not found."}
    
    if checkUser.verification == 0:
        return{"status":0,"msg":"please verify your email id"}

    password_verification = verify_password(password,checkUser.password)
     
    if not password_verification:
        return {"status":0,"msg":"Password  worng."}

    else:
        char1 = 'qwertyuioplkjhgfdsazxcvbnm1234567890'
        char2 = 'QWERTYUIOPLKJHGFDSAZXCVBNM0123456789'
        reset_character = char1 + char2
        key = ''.join(random.choices(reset_character, k=30))
        
        token =f"{key}nTew20drhkl"
    
        create_token = Apitoken(
            user_id = checkUser.user_id,
            token = token,
            status = 1
        )
        db.add(create_token)
        db.commit()
        
        return {"status":1,"msg":"Login successfully","token":token}
    
@router.post("/update-profile")
async def update_profile(
    token:str =Form(...),
    db:Session=Depends(deps.get_db),
    first_name: str = Form(None),
    last_name: str = Form(None),
    username : str =Form(None),
    email: str = Form(None),
    old_password : str =Form(None),
    new_password :str =Form(None),
    phone_number: str = Form(None)
):
    check_token=deps.get_token(token,db)
    if not check_token:
        return {"status": 0 ,"msg":"Invalid Token"}
      
    if first_name:
       check_token.first_name = first_name
    if last_name:
       check_token.last_name = last_name

    if username:
        check_username = db.query(User).filter(User.username == username).first()
        if check_username:
            return {"status": 0, "msg":"User_Name already exists"}
        check_token.username = username


    if email:
        check_email = db.query(User).filter(User.email == email).first()
        if check_email:
            return {"status":0, "msg":"Email already exists"}
        check_token.email = email
        check_token.verification=0
    

    if old_password:
        check_password =verify_password(old_password, check_token.password)
        if not check_password:
            return {"status":0, "msg":"Old_password wrong"}
        check_token.password = get_password_hash(new_password)
      

    if phone_number:
        mobile_number = deps.mobile_number_verify(phone_number)
        if not mobile_number:
            return {"status":0,"msg":"please fill the 10 digit mobile number"}
        check_phone = db.query(User).filter( User.phone_number == phone_number).first()
        if check_phone:
            return {"status":0,"msg":"Phone number already exists"}
        check_token.phone_number = phone_number

    db.commit()
    return {"status":1,"msg":"Profile updated successfully and your email update means verfied the Email Id otherwise not allow to login"}

@router.post("/logout-user")
async def logout_user(token:str=Form(...), 
                 db:Session=Depends(deps.get_db)):
    check_token = deps.get_token(token,db)
    if not check_token:
        return {"status":0,"msg":"Invalid token"}
    expired=db.query(Apitoken).filter(Apitoken.user_id==check_token.user_id,Apitoken.status==1).first()
    expired.status=2 
    db.commit()
    return {"status": 1, "msg": "Successfully logged out"}

 
    