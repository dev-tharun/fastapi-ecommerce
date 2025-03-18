from fastapi import APIRouter
from .endpoints import signup,cateogry,brand,subcategories,product,add_to_cart,orders,wishlist

api_router = APIRouter()

api_router.include_router(signup.router, tags=["Signup"])
api_router.include_router(brand.router, prefix='/brand',tags=['Brands'])
api_router.include_router(cateogry.router, prefix='/category',tags=['Category'])
api_router.include_router(subcategories.router, prefix='/sub-category',tags=['Subcategories'])
api_router.include_router(product.router, prefix='/product',tags=['Product'])
api_router.include_router(add_to_cart.router, prefix='/cart',tags=['Cart'])
api_router.include_router(wishlist.router, prefix='/wishlist',tags=['Wishlist'])
api_router.include_router(orders.router, prefix='/order',tags=['Order'])


