from fastapi import APIRouter, Depends, Form
from sqlalchemy.orm import Session
from app.models import *
from app.api import deps
from app.utils import *

router = APIRouter()

@router.post("/create-subcategory")
async def create_subcategory(token:str=Form(...),
                        category_product_id: int = Form(...),
                        sub_category_name:str=Form(...),
                        sub_category_description:str=Form(...),
                        db:Session=Depends(deps.get_db)):
    
    check_token=deps.get_token(token,db)

    if not check_token:
        return {"status":0,"msg":"invalid token"}
    
    if check_token.user_type != 2:
        return {"status":0,"msg":"User not authorized"}
    
    category = db.query(CategoryProduct).filter(CategoryProduct.category_product_id==category_product_id)
    if not category:
        return {"status":0,"msg":"Category not found"}
    
    create_sub_category=SubCategory(
        category_product_id=category_product_id,
        sub_category_name=sub_category_name,
        sub_category_description=sub_category_description,
        status=1
        )
    db.add(create_sub_category)
    db.commit()

    return {"status":1,"msg":"sucessfully add subcategory"}


@router.post("/subcategory-list")
async def subcategory_list( token:str=Form(...),page:int=1,size:int=10,
                      db: Session = Depends(deps.get_db)):
    
    check_token = deps.get_token(token,db)
    if not check_token:
        return {"status": 0,"msg":"Invalid token"}
    
    subcategory_list=db.query(SubCategory).filter(SubCategory.status==1)
    row_count = subcategory_list.count()
    total_pages,offset,limit = get_pagination(row_count,page,size)
    paginated_subcategory= subcategory_list.offset(offset).limit(limit).all()

    data=[]
    for subcategory in paginated_subcategory:
        data.append({"sub_category_id":subcategory.sub_category_id,
                     "category_product_id ":subcategory.category_product_id ,                    
                    "sub_category_name": subcategory.sub_category_name,
                     "sub_category_description":subcategory.sub_category_description})
    return{
        "status": 1,
        "total_subcategory": row_count,
        "total_pages": total_pages,
        "current_page": page,
        "page_size": size,
        "subcategory":data
    }

@router.post("/update-subcategory")
async def update_subcategory(
    token: str = Form(...),
    sub_category_id: int =Form(...),
    sub_category_name: str =Form(None),
    sub_category_description: str = Form(None),
    db: Session = Depends(deps.get_db)
):
    check_token = deps.get_token(token,db)

    if not check_token:
        return {"status": 0, "msg": "Invalid token"}

    if check_token.user_type != 2:
        return {"status": 0, "msg": "User not authorized"}

    sub_category = db.query(SubCategory).filter(SubCategory.sub_category_id==sub_category_id,SubCategory.status==1).first()
    if not sub_category:
        return {"status": 0, "msg": "Subcategory not found"}

    if sub_category_name is not None:
        sub_category.sub_category_name = sub_category_name
    if sub_category_description is not None:
        sub_category.sub_category_description = sub_category_description
    db.commit()
        
    return {"status": 1, "msg": "Subcategory successfully updated"}

@router.post("/delete-subcategory")
async def delete_subcategory( token:str=Form(...),
                      sub_category_id:int=Form(...),
                      db: Session = Depends(deps.get_db)):
    
    check_token = deps.get_token(token, db)

    if not check_token:
        return {"status": 0, "msg": "Invalid token"}

    if check_token.user_type != 2:
        return {"status": 0, "msg": "User not authorized"}

    sub_category = db.query(SubCategory).filter(SubCategory.sub_category_id==sub_category_id).first()
    if not sub_category:
        return {"status":0,"msg":"Subcategory not found"}
    sub_category.status=-1
    db.commit()
        
    return {"status":1,"msg":"Subcategory successfully deleted"}
        
    



