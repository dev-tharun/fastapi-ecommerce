from fastapi import APIRouter, Depends, Form
from sqlalchemy.orm import Session
from app.models import *
from app.api import deps
from app.utils import *

router = APIRouter()

@router.post("/create-wishlist")
async def create_wishlist(
    token:str=Form(...),
    product_id:int=Form(...),
    db:Session=Depends(deps.get_db)
):
    check_token=deps.get_token(token,db)
    if not check_token:
        return {"status":0,"msg":"Invalid token"}
    
    product = db.query(Product).filter(Product.product_id==product_id,Product.status==1).first()
    if not product:
        return {"status":0,"msg":"Product not found"}
    
    wishlist=db.query(Wishlist.product_id==product_id,Wishlist.status==1).first()
    if wishlist:
        return {"status":0, "msg":"already wishlist added"}
    
    wishlist_item = Wishlist(
        product_id=product_id,
        user_id=check_token.user_id,
        status=1
    )
    db.add(wishlist_item)
    db.commit()
    
    return {"status":1,"msg":"Successfully added to wishlist"}

@router.post("/list-wishlist")
async def list_wishlist(
    token:str=Form(...),
    page:int=1,
    size:int=10,
    wishlist:str=Form(None),
    db:Session=Depends(deps.get_db)
):
    check_token=deps.get_token(token, db)
    if not check_token:
        return {"status":0,"msg":"Invalid token"}
    
    wishlist_list=db.query(Wishlist).join(Product,Product.product_id==Wishlist.product_id).filter(Wishlist.user_id==check_token.user_id,Wishlist.status==1)
    if wishlist:
        wishlist_list=wishlist_list.filter(Product.product_name.like(f"{wishlist}%"))

    row_count = wishlist_list.count()    
    total_pages,offset,limit=get_pagination(row_count, page, size)
    paginated_wishlist=wishlist_list.offset(offset).limit(limit).all()
    
    data = []
    for wishlist in paginated_wishlist:
        data.append({
            "wishlist_id": wishlist.wishlist_id,
            "user_id": wishlist.user_id,
            "product_id": wishlist.product_id,
            "user_name": wishlist.user.username,
            "product_name": wishlist.product.product_name,
            "product_description": wishlist.product.product_description,
            "product_price":wishlist.product.discount_product_price
        })
    
    return {
        "status": 1,
       "total_wishlist": row_count,
        "total_pages": total_pages,
        "current_page": page,
        "page_size": size,
        "wishlist": data
    }

@router.post("/delete-wishlist")
async def delete_wishlist(
    wishlist_id:int=Form(...),
    token:str=Form(...),
    db:Session=Depends(deps.get_db)):
    check_token=deps.get_token(token, db)
    if not check_token:
        return {"status":0,"msg": "Invalid token"}
    
    wishlist_item=db.query(Wishlist).filter(Wishlist.wishlist_id==wishlist_id,Wishlist.user_id==check_token.user_id).first()
    if not wishlist_item:
        return {"status":0,"msg":"Wishlist item not found"}
    wishlist_item.status=-1
    db.commit()
    
    return {"status": 1, "msg": "Wishlist item deleted successfully"}
