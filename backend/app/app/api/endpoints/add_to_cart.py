from fastapi import APIRouter, Depends, Form
from sqlalchemy.orm import Session
from app.models import *
from app.api import deps
from app.utils import *

router = APIRouter()

@router.post("/create-cart")
async def create_cart(
    token: str=Form(...),
    product_id:int= Form(...),
    quantity:int=Form(...,ge=1),
    db:Session=Depends(deps.get_db)
):
    check_token = deps.get_token(token, db)

    if not check_token:
        return {"status":0,"msg":"Invalid token"}

    product = db.query(Product).filter(Product.product_id== product_id,Product.status==1).first()
    if not product:
        return {"status": 0, "msg":"Product not found"} 
    
    if product.product_stock < quantity:
        return {"status" : 0,"msg":"stock not available"}
    
    cart=db.query(Cart).filter(Cart.product_id==product_id,Cart.status==1,Cart.user_id==check_token.user_id).first()
    if cart:
         return {"status":0, "msg":"already product added"}
       
    total_price = product.discount_product_price*quantity  
    create_cart=Cart(
        product_id=product_id,
        user_id=check_token.user_id,
        quantity=quantity,
        price=total_price,
        status=1
    )
    db.add(create_cart)
    db.commit()

    return {
        "status":1,
         "msg":"Successfully added cart",   
    }

@router.post("/list-cart")
async def list_cart(
                    token:str=Form(...),
                    page:int=1,
                    size:int=10,
                    db:Session=Depends(deps.get_db)):
    
    check_token = deps.get_token(token, db)
    if not check_token:
        return {"status":0,"msg":"Invalid token"}
    cart_list=db.query(Cart).filter(Cart.status==1,Cart.user_id==check_token.user_id)
    row_count = cart_list.count()
    total_pages,offset,limit = get_pagination(row_count,page,size)
    paginated_cart= cart_list.offset(offset).limit(limit).all()
    
    data=[]
    total_amount=0
    for cart_lists in paginated_cart:
        total_sum =  cart_lists.price 
        total_amount   +=   total_sum
        data.append({
            "cart id":cart_lists.cart_id,
            "user_id":cart_lists.user_id,
            "product_id":cart_lists.product_id,
            "user_name":cart_lists.user.username,
            "product_name":cart_lists.product.product_name,
            "product_description":cart_lists.product.product_description,
            "original_price":cart_lists.product.product_price,
            "discount":cart_lists.product.product_discount,
            "product_discount_price":cart_lists.product.discount_product_price,
            "quantity":cart_lists.quantity,
            "price":cart_lists.price,
        })

    return {
                "status": 1,
                "total_cart": row_count,
                "total_pages": total_pages,
                "current_page": page,
                "page_size": size,
                "cart": data,
                "total_amount":total_amount
               }

       
@router.post("/update-cart")
async def update_cart(
    cart_id: int=Form(...),
    token: str = Form(...),
    quantity: int = Form(None,ge=1),
    db: Session = Depends(deps.get_db)
):
    check_token = deps.get_token(token, db)
    if not check_token:
        return {"status":0,"msg":"Invalid token"}

    cart_item=db.query(Cart).filter(Cart.cart_id==cart_id,Cart.user_id==check_token.user_id,Cart.status==1).first()
    if not cart_item:
        return {"status":0,"msg":"Cart item not found"}

    product=db.query(Product).filter(Product.product_id==cart_item.product_id,Product.status==1).first()
    if not product:
        return {"status":0,"msg":"Product not found"}
     
    if cart_item is not None:
        cart_item.quantity  =  quantity
        cart_item.price=product.discount_product_price*quantity
    db.commit()

    return {"status": 1,"msg":"Cart updated successfully"}

@router.post("/delete-cart")
async def delete_cart(
    cart_id: int,
    token: str=Form(...),
    db: Session = Depends(deps.get_db)
):
    check_token = deps.get_token(token, db)
    if not check_token:
        return {"status": 0,"msg":"Invalid token"}

    cart_item = db.query(Cart).filter(Cart.cart_id==cart_id,Cart.user_id==check_token.user_id).first()
    if not cart_item:
        return {"status":0,"msg":"Cart item not found"}
    cart_item.status=-1
    db.commit()

    return {"status": 1,"msg":"Cart deleted successfully"}

