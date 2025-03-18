from fastapi import APIRouter, Depends, Form
from sqlalchemy.orm import Session
from app.models import *
from app.api import deps
from app.utils import *

router = APIRouter()

@router.post("/create-brand")
async def create_brand(token:str=Form(...),
                      brand_name:str=Form(...),
                      brand_description:str=Form(...),
                      db:Session=Depends(deps.get_db),):
    
    check_token=deps.get_token(token,db)
    
    if not check_token:
        return {"status":0,"msg":"invalid token"}
    
    if check_token.user_type != 2:
        return {"status":0,"msg":" User not authorized"}
    
    create_brand=Brand(
            brand_name=brand_name.strip(),
            brand_description=brand_description,
            status=1
        )
    db.add(create_brand)
    db.commit()

    return {"status":1,"msg":"Brand sucessfully added"}

@router.post("brand_list")
async def brand_list( token:str=Form(...),
                     page:int=1,
                     size:int=10,
                     brand_name:str=Form(None),
                     db: Session=Depends(deps.get_db)):
    
    check_token = deps.get_token(token, db)

    if not check_token:
        return {"status": 0,"msg":"Invalid token"}
          
    brand_list=db.query(Brand).filter(Brand.status==1)
    if brand_name:
        brand_list=brand_list.filter(Brand.brand_name.like(f"{brand_name}%"))

    row_count = brand_list.count()
    total_pages,offset,limit = get_pagination(row_count,page,size)
    paginated_brands= brand_list.offset(offset).limit(limit).all()

    data=[]
    for brand_list in paginated_brands:
        data.append({"brand_id":brand_list.brand_id,
                     "brand_name":brand_list.brand_name,
                     "brand_description":brand_list.brand_description})    
    return{
        "status": 1,
        "total_brand": row_count,
        "total_pages": total_pages,
        "current_page": page,
        "page_size": size,
        "brands": data
        }

@router.post("/update-brand")
async def update_brand(
    token: str = Form(...),
    brand_id: int=Form(...),
    brand_name: str =Form(None),
    brand_description: str = Form(None),
    db: Session = Depends(deps.get_db),
):
    check_token = deps.get_token(token, db)

    if not check_token:
        return {"status":0, "msg":"Invalid token"}
    
    if check_token.user_type != 2:
        return {"status":0, "msg":"User not authorized"}

    brand = db.query(Brand).filter( Brand.brand_id == brand_id,Brand.status == 1).first()
    if not brand:
        return {"status":0,"msg":"Brand not found"}
    
    
    if brand_name is not None:
        brand.brand_name = brand_name
    if brand_description is not None:
        brand.brand_description = brand_description
    db.commit()
  
    return {"status":1,"msg":"Brand successfully updated"}

@router.post("/delete-brand")
async def delete_brand(
    brand_id: int=Form(...),
    token: str = Form(...),
    db: Session = Depends(deps.get_db),
):
    check_token = deps.get_token(token, db)

    if not check_token:
        return {"status":0,"msg":"Invalid token"}
    
    if check_token.user_type != 2:
        return {"status":0,"msg":"User not authorized"}

    brand = db.query(Brand).filter(Brand.brand_id==brand_id).first()
    if not brand:
        return {"status":0,"msg":"Brand not found"}
    
    brand.status= -1
    db.commit()
  
    return {"status":1,"msg":"Brand successfully deleted"}


