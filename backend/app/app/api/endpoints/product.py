from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session
from app.models import *
from app.api import deps
from app.utils import *

router = APIRouter()


@router.post("/create-product")
async def create_product(
    token: str=Form(...),
    brand_id: int =Form(...),
    sub_category_id: int =Form(...),
    category_product_id: int =Form(...),
    product_name: str =Form(...),
    product_stock: int =Form(...),
    product_price: float =Form(...),
    product_discount: float =Form(default=0.0),
    product_description: str =Form(...),
    image_url:list[UploadFile]=File(...),
    db:Session = Depends(deps.get_db),
):
    check_token = deps.get_token(token, db)
    
    if not check_token:
        return {"status":0,"msg":"invalid token"}
    
    if check_token.user_type != 2:
        return {"status":0,"msg":"User not authorized"}
    
    brand = db.query(Brand).filter(Brand.brand_id==brand_id,Brand.status==1).first()
    if not brand:
        return {"status":0,"msg":"Brand not found"}
    
    category = db.query(CategoryProduct).filter(CategoryProduct.category_product_id==category_product_id,CategoryProduct.status==1).first()
    if not category:
        return {"status":0,"msg":"Category not found"}
    
    sub_category = db.query(SubCategory).filter(SubCategory.sub_category_id==sub_category_id,SubCategory.status==1).first()
    if not sub_category:
        return {"status":0,"msg":"SubCategory not found"}
    
    
    discount_product_price =product_price * (1 - (product_discount/100))
    create_product = Product(
            brand_id=brand_id,
            sub_category_id=sub_category_id,
            category_product_id=category_product_id,
            product_name=product_name,
            product_stock=product_stock,
            product_price=product_price,
            product_discount=product_discount,
            discount_product_price=discount_product_price,
            product_description=product_description,
            status=1,

        )
    db.add(create_product)
    db.commit()
    
    stored_image_path = deps.save_images(image_url, create_product.product_id)

    for image_path in stored_image_path:
        product_image = ProductImage(
                product_id=create_product.product_id,
                productimage_url=image_path,
                status=1
            )
        db.add(product_image)
    db.commit()

    return {"status":1,
            "message":"Product created successfully",
              "image":stored_image_path}
   
@router.post("/list-products")
async def list_products(
    token: str=Form(...),
    brand:str=Form(None),
    cateogry:str=Form(None),
    subcategory:str=Form(None),
    product:str=Form(None),
    from_price=Form(None),
    to_price=Form(None),
    high_low_or_low_high:bool=Form(None,description="filter price True - high to low , False low to high "),
    page:int=1,
    size:int=10,
    db:Session=Depends(deps.get_db),
):
    
    check_token = deps.get_token(token, db)
    
    if not check_token:
        return {"status": 0, "msg": "Invalid token"}
    
    if high_low_or_low_high:
        list =(
            db.query(Product)
            .join(Brand,Brand.brand_id==Product.brand_id)
            .join(CategoryProduct,CategoryProduct.category_product_id==Product.category_product_id)
            .join(SubCategory,SubCategory.sub_category_id==Product.sub_category_id)
            .filter( Product.status==1)
            .order_by(Product.discount_product_price.desc())) # true high to low
    else:
        list =(
            db.query(Product)
            .join(Brand,Brand.brand_id==Product.brand_id)
            .join(CategoryProduct,CategoryProduct.category_product_id==Product.category_product_id)
            .join(SubCategory,SubCategory.sub_category_id==Product.sub_category_id)
            .filter( Product.status==1)
            .order_by(Product.discount_product_price.asc())) #false low to high
    
    if brand:
       list= list.filter(Brand.brand_name.like(f"{brand}%"))
    if cateogry:
        list=list.filter(CategoryProduct.category_product_name.like(f"{cateogry}%"))
    if subcategory:
       list= list.filter(SubCategory.sub_category_name.like(f"{subcategory}%"))
    if product:
       list= list.filter(Product.product_name.like(f"{product}%"))
    if from_price:
        list = list.filter(Product.product_price>=from_price)
    if to_price:
        list = list.filter(Product.product_price<=to_price)

    row_count = list.count()
    total_pages,offset,limit = get_pagination(row_count,page,size)
    paginated_product= list.offset(offset).limit(limit).all()

    data = []
   
    for list_of_product in paginated_product:
        data.append({
            "product_id": list_of_product.product_id,
            "brand_name": list_of_product.brand.brand_name,
            "product_name": list_of_product.product_name,
            "Product_description":list_of_product.product_description,
            "product_price":list_of_product.product_price,
            "product_discount":f"{list_of_product.product_discount}%",
            "discount_price": list_of_product.discount_product_price,
            "category_name": list_of_product.category_product.category_product_name,
            "subcategory_name": list_of_product.sub_category.sub_category_name,
        })
    
    return {
        "status":1,
        "total_product": row_count,
        "total_pages": total_pages,
        "current_page": page,
        "page_size": size,
        "Products": data
    }

@router.post("/view-product")
async def view_product(token:str=Form(...), 
                       product_id:int=Form(...), 
                       db:Session=Depends(deps.get_db)):

    check_token = deps.get_token(token, db)
    
    if not check_token:
        return {"status":0,"msg": "Invalid token"}
    
    product = db.query(Product).filter(Product.product_id == product_id).first()
    if not product:
        return {"status":0,"msg":"Product not found"}

    product_images = db.query(ProductImage).filter(ProductImage.product_id == product_id)
    if not product_images:
        return {"status": 0,"msg":"No images available for this product"}

    image_urls=[]
    for img in product_images:
        image_urls.append({"image_url":img.productimage_url})

    return {
        "status": 1,
        "product_name": product.product_name,
        "price": product.product_price,
        "brand_name": product.brand.brand_name,
        "category_name": product.category_product.category_product_name,
        "subcategory_name": product.sub_category.sub_category_name,
         "images": image_urls
    }

@router.post("/update-product")
async def update_product(
    token:str = Form(...),
    product_id:int=Form(...),
    brand_id:int = Form(None),
    sub_category_id:int =Form(None),
    category_product_id:int =Form(None),
    product_name:str =Form(None),
    product_stock:int =Form(None),
    product_discount:float =Form(None),
    product_price:float =Form(None),
    product_description:str=Form(None),
    db:Session=Depends(deps.get_db),
):
    check_token = deps.get_token(token, db)
    
    if not check_token:
        return {"status": 0, "msg": "Invalid token"}
    
    if check_token.user_type != 2:
        return {"status": 0, "msg": "User not authorized"}
    
    product = db.query(Product).filter(Product.product_id == product_id,Product.status==1).first()
    if not product:
        return {"status": 0, "msg": "Product not found"}
   
    if product_name is not None:
        product.product_name=product_name

    if brand_id is not None:
        product.brand_id=brand_id

    if sub_category_id is not None:
            product.sub_category_id=sub_category_id

    if category_product_id is not None:
            product.category_product_id=category_product_id

    if product_stock is not None:
            product.product_stock+=product_stock

    if product_price is not None:
            product.product_price=product_price
            product.discount_product_price=product.product_price*(1-(product.product_discount/100))    

    if product_discount is not None:
           product.product_discount=product_discount
           product.discount_product_price=product.product_price*(1-(product.product_discount/100))
     
    if product_description is not None:
            product.product_description = product_description
        
    cart_item=db.query(Cart).filter(Cart.product_id==product_id,Cart.status==1).all()
    if cart_item:
        for cart in cart_item:
           cart.price = cart.quantity * product.discount_product_price

    wishlist_item=db.query(Wishlist).filter(Wishlist.product_id==product_id,Wishlist.status==1).all()
    if wishlist_item:
        for wishlist in wishlist_item:
            wishlist.product_id = product_id

    db.commit()
       
    return {"status":1,"msg":"Successfully updated product"}

@router.post("/delete-product")
async def update_product(
    product_id: int=Form(...),
    db: Session = Depends(deps.get_db),
):
    check_token = deps.get_token(token, db)
    
    if not check_token:
        return {"status":0,"msg":"Invalid token"}
    
    if check_token.user_type != 2:
        return {"status":0,"msg":"User not authorized"}
    
    product=db.query(Product).filter(Product.product_id==product_id).first()
    if not product:
        return {"status":0,"msg":"Product not found"}
    
    product.status=-1
    db.commit()
    return {"status":1,"msg":"Successfully deleted product"}




