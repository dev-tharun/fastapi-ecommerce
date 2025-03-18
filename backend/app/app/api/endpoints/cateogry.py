from fastapi import APIRouter, Depends, Form
from sqlalchemy.orm import Session
from app.models import *
from app.api import deps
from app.utils import *

router = APIRouter()

@router.post("/create-category")
async def create_category(token:str=Form(...),
                        category_product_name:str=Form(...),
                        category_product_description:str=Form(...),
                        db:Session=Depends(deps.get_db)):
    
    check_token=deps.get_token(token,db)
    if not check_token:
        return {"status":0,"msg":"invalid token"}
    
    if check_token.user_type != 2:
        return {"status":0,"msg":" User not authorized"}
    
    create_category_product=CategoryProduct(
        category_product_name=category_product_name,
        category_product_description=category_product_description,
        status=1
        )
    db.add(create_category_product)
    db.commit()

    return {"status":1,"msg":"sucessfully add category_product"}


@router.post("/category-list")
async def category_list( token:str=Form(...),page:int=1,size:int=10,
                      db: Session = Depends(deps.get_db)):
    
    check_token = deps.get_token(token, db)

    if not check_token:
        return {"status": 0,"msg":"Invalid token"}
    
    category_list=db.query(CategoryProduct).filter(CategoryProduct.status==1)
    row_count = category_list.count()
    total_pages,offset,limit = get_pagination(row_count,page,size)
    paginated_category= category_list.offset(offset).limit(limit).all()
    data=[]
    for category_list in paginated_category:
        data.append({"category_id":category_list.category_product_id,
                    "category_product_name": category_list.category_product_name,
                     "category_product_description":category_list.category_product_description})
        
    return {
        "status": 1,
        "total_category": row_count,
        "total_pages": total_pages,
        "current_page": page,
        "page_size": size,
        "category": data
    }

@router.post("/update-category")
async def update_category( token:str=Form(...),
                      category_id:int=Form(...),
                      category_product_name:str=Form(None),
                      category_product_description:str=Form(None),
                      db: Session = Depends(deps.get_db)):
    
    check_token = deps.get_token(token, db)

    if not check_token:
        return {"status": 0,"msg":"Invalid token"}
    
    if check_token.user_type != 2:
        return {"status":0, "msg":"User not authorized"}
    
    category_product=db.query(CategoryProduct).filter(CategoryProduct.category_product_id==category_id,CategoryProduct.status==1).first()
    if not category_product:
        return {"status":0, "msg": "category_product not found"}
    
    if category_product is not None:
         category_product.category_product_name=category_product_name
    if category_product_description is not None:
        category_product.category_product_description= category_product_description
    db.commit()

    return {"status": 1, "msg": "cateogry successfully updated"}

@router.post("/delete-category")
async def delete_category( token:str=Form(...),
                      category_id:int=Form(...),
                      db: Session = Depends(deps.get_db)):
    
    check_token = deps.get_token(token, db)

    if not check_token:
        return {"status": 0,"msg":"Invalid token"}
    
    if check_token.user_type != 2:
        return {"status":0, "msg":"User not authorized"}
    
    category_product=db.query(CategoryProduct).filter(CategoryProduct.category_product_id==category_id).first()
    if not category_product:
        return {"status":0, "msg": "category_product not found"}
    
    category_product.status=-1
    db.commit()

    return {"status": 1, "msg": "cateogry successfully deleted"}
       
       
    
        
    
