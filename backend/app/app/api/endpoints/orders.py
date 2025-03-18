from fastapi import APIRouter, Depends, Form
from fpdf import FPDF
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.models import *
from app.api import deps
from app.utils import *

router = APIRouter()

@router.post("/create-order")
async def create_order(token:str=Form(...),
                       cart_id:str=Form(None,description="mutilple  product order to place"),
                       product_id:str=Form(None,description="only for single product order to place"),
                       product_quantity:int=Form(None,ge=1),
                       user_address:str=Form(...),
                       city:str=Form(...),
                       pincode:str=Form(...),
                       payment_method:int=Form(...,description="1-cash 2-online"),
                       db:Session=Depends(deps.get_db)
                       ):
    
    check_token=deps.get_token(token,db)
    if not check_token:
        return {"status":0,"msg":"invalid token"}
   
    if cart_id:
            cart_ids=[]
            for cart in cart_id.split(","):
                cart_ids.append(cart)
            cart=db.query(Cart).filter(Cart.cart_id.in_(cart_ids),Cart.status==1).all()
        
            create_order = Order(
                user_id=check_token.user_id,
                user_address=user_address,
                city=city,
                pincode=pincode,
                order_date=func.current_date(),
                status=1,  
            )
            db.add(create_order)
            db.commit()

            for cart_item in cart:

                product = db.query(Product).filter(Product.product_id==cart_item.product_id,Product.status==1).first()
                if not product:
                    return {"status":0,"msg":"product id not found"}
                if product.product_stock<cart_item.quantity:
                    return{"status":0,"msg":"product stock not available"}
            
                product.product_stock -= cart_item.quantity
                order_detail =OrderDetails(
                        order_id=create_order.order_id,
                        product_id=cart_item.product_id ,
                        quantity=cart_item.quantity,
                        order_price=cart_item.price,
                        status=1,
                    )
                db.add(order_detail)
            db.commit()
        
            total_amount =deps.calculate_total_amount(db,create_order.order_id)
            create_bill = Bill(
            user_id=check_token.user_id,
            order_id=create_order.order_id,
            payment_method="Cash "if payment_method == 1 else "Online",
            bill_address=user_address,
            total_amount=total_amount,
            date=func.current_date(),
            status=1)
            db.add(create_bill)
            db.commit()
         
    elif product_id:
            create_order = Order(
                user_id=check_token.user_id,
                user_address=user_address,
                city=city,
                pincode=pincode,
                order_date=func.current_date(),
                status=1)
            db.add(create_order)
            db.commit()

            product = db.query(Product).filter(Product.product_id==product_id,Product.status==1).first()

            if not product:
                return {"status":0,"msg":"product id not found"}
            if product.product_stock  < product_quantity:
                return{"status":0,"msg":"product stock not available"}
            
            product.product_stock -= product_quantity
            order_detail =OrderDetails(
                    order_id=create_order.order_id,
                    product_id=product_id ,
                    quantity=product_quantity,
                    order_price=product.discount_product_price,
                    status=1,
                )
            db.add(order_detail)
            db.commit()

            total_amount=deps.calculate_total_amount(db,create_order.order_id)
            create_bill = Bill(
            user_id=check_token.user_id,
            order_id=create_order.order_id,
            payment_method="Cash "if payment_method == 1 else "Online",
            bill_address=user_address,
            total_amount=total_amount,
            date=func.current_date(),
            status=1)
            db.add(create_bill)
            db.commit()      

    return {"status":1,"msg":"Order placed successfully", 
            "order_id":create_order.order_id, 
            "total_amount": total_amount,
    }

@router.post("/orders-list")
async def orders_list(token:str=Form(...), 
                            date:date=Form(None),
                            order_status:int=Form(None,description= "1 - Confirm  2 - Cancel 3 - Ship  4 - Deliver 5 - Return"),
                            page:int=1,
                            size:int=10,
                            order_id:int=Form(None),
                            db:Session=Depends(deps.get_db)):
    check_token = deps.get_token(token, db)
    if not check_token:
        return {"status":0,"msg":"Invalid token"}

    order_items= (
        db.query(Order)
        .join(OrderDetails, OrderDetails.order_id==Order.order_id)
        .filter(Order.user_id == check_token.user_id, Order.status !=-1))
    
    if date:
        order_date = datetime.strftime(date,"%Y-%m-%d")
        order_items = order_items.filter(Order.order_date.like(f"%{order_date}%"))

    if order_id:
        order_items=order_items.filter(Order.order_id==order_id)

    if order_status:
        order_items=order_items.filter(Order.status==order_status)
     
    row_count=order_items.count()
    total_pages, offset, limit = get_pagination(row_count, page, size)
    paginated_order = order_items.offset(offset).limit(limit).all()

    data=[]
    for order in paginated_order:
        order_data={
            "order_id": order.order_id,
            "user_name": order.user.username,
            "user_address": order.user_address,
            "city": order.city,
            "pincode": order.pincode,
            "order_date": order.order_date,
            "status": order.status,
            "products":[]
        }
        for order_detail in order.order_details:
            product_data = {
                "product_id":order_detail.product.product_id,
                "product_name":order_detail.product.product_name,
                "original_price":order_detail.product.product_price,
                "discount":f"{order_detail.product.product_discount}%",
                "discount_price": order_detail.product.discount_product_price,
                "quantity":order_detail.quantity,
                "Order_price":order_detail.order_price,
            }
            order_data["products"].append(product_data)

        data.append(order_data)    

    return {
        "status" :1,
        "total_order": row_count,
        "total_pages": total_pages,
        "current_page": page,
        "page_size": size,
        "order_items": data,
    }

@router.post("/cancel-order")
async def cancel_order(order_id:int=Form(), 
                       token:str=Form(...), 
                      db:Session=Depends(deps.get_db)):
    check_token=deps.get_token(token, db)
    if not check_token:
        return {"status":0,"msg":"Invalid token"}

    order=db.query(Order).filter(Order.order_id==order_id,Order.user_id==check_token.user_id).first()
    if not order:
        return {"status":0,"msg":"Order not found"}

    if order.status==2:
        return {"status":0,"msg":"Order is already canceled"}
    order.status=2  
    db.commit()

    order_details=db.query(OrderDetails).filter(OrderDetails.order_id==order_id).all()
    for item in order_details:
        product=db.query(Product).filter(Product.product_id==item.product_id).first()
        if product:
            product.product_stock   +=   item.quantity  
        item.status=2  
    db.commit()

    return {"status": 1,"msg":"Order canceled successfully"}

@router.post("/ship-order")
async def ship_order(order_id:int=Form(), 
                     token:str=Form(...), 
                     db:Session=Depends(deps.get_db)):
    check_token=deps.get_token(token, db)
    if not check_token:
        return {"status": 0,"msg":"Invalid token"}

    order = db.query(Order).filter(Order.order_id == order_id,Order.status==1).first()
    if not order:
        return {"status": 0, "msg":"Order not found"}
    
    if order.status == 3:
        return {"status":0,"msg":"Order is already ship"}

    order.status=3  
    db.commit()
    return {"status": 1, "msg":"Order shipped successfully"}

@router.post("/deliver-order")
async def deliver_order(order_id:int=Form(), 
                        token:str=Form(...), 
                        db:Session=Depends(deps.get_db)):
    check_token=deps.get_token(token, db)
    if not check_token:
        return {"status": 0,"msg":"Invalid token"}

    order = db.query(Order).filter(Order.order_id==order_id,Order.status==3).first()
    if not order:
        return {"status": 0,"msg":"Order not found"}
    
    if order.status == 4:
        return {"status": 0,  "msg":"Order is already deliver"}
    order.status=4 
    order.delivered_at=datetime.now()
    db.commit()
    return {"status":  1,  "msg":"Order delivered successfully"}

@router.post("/return-order")
async def return_order(order_id:int=Form(), 
                       token:str=Form(...), 
                       db:Session=Depends(deps.get_db)):
    check_token = deps.get_token(token, db)
    if not check_token:
        return {"status": 0, "msg": "Invalid token"}

    order = db.query(Order).filter(Order.order_id==order_id,Order.status==4).first()
    if not order:
        return {"status": 0, "msg": "Order not found"}

    if not order.delivered_at:
        return {"status": 0, "msg": "Delivery time not recorded"}
    
    if order.status == 5:
        return {"status":0,"msg":"Order is already return"}

    current_time = datetime.now()
    delivered_time=order.delivered_at

    current_seconds   =  current_time.hour*3600      +    current_time.minute*60     +  current_time.second
    delivered_seconds =  delivered_time.hour*3600  +  delivered_time.minute*60     +  delivered_time.second

    time  =  current_seconds  -  delivered_seconds
   
    if time >= 60:
        return {"status": 0,"msg":"Return allowed only within 1 minute of delivery"}

    order.status=5  
    db.commit()
    return {"status":1,"msg":"Order return successfully"}

LOCAL_STORAGE_PATH="C:/Users/tharu/Desktop/bills_pdf"
os.makedirs(LOCAL_STORAGE_PATH, exist_ok=True)

@router.post("/invoice-pdf")
async def invoice_pdf(token:str=Form(...),
                            order_id: int=Form(...), 
                            db: Session = Depends(deps.get_db)):

    check_token = deps.get_token(token, db)
    if not check_token:
        return {"status":0,"msg":"Invalid token"}
   
    order=db.query(Order).filter(Order.order_id==order_id,Order.user_id==check_token.user_id,Order.status==1).first()
    if not order:
        return {"status": 0, "msg":"Order not found"}
    
    bill=db.query(Bill).filter(Bill.order_id==order_id,Bill.status==1).first()
    if not bill:
        return {"status": 0, "msg":"Bill already generated for this order"}

    order_items =db.query(OrderDetails).filter(OrderDetails.order_id==order_id,OrderDetails.status==1).all()
    if not order_items:
        return {"status": 0, "msg": "No order items found"}

   
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)

 
    pdf.cell(200, 10, "-----------------------------------------------------", ln=True, align="C")
    pdf.cell(200, 10, "      Get an invoice", ln=True, align="C")
    pdf.cell(200, 10, "-----------------------------------------------------", ln=True, align="C")
    pdf.ln(10)


    pdf.cell(200, 10, f"Customer: {check_token.first_name.capitalize()} {check_token.last_name.capitalize()}", ln=True)
    pdf.cell(200, 10, f"Address: {order.user_address}", ln=True)
    pdf.cell(200, 10, f"City: {order.city}", ln=True)
    pdf.cell(200, 10, f"Pin-code: {order.pincode}", ln=True)
    pdf.cell(200, 10, f"Order-Date: {order.order_date}", ln=True)
    pdf.cell(200, 10, f"Order ID: {order.order_id}", ln=True)
    pdf.ln(10)


    pdf.cell(80, 10, "Product")
    pdf.cell(20, 10, "Qty")
    pdf.cell(30, 10, "Orig. Price")
    pdf.cell(30, 10, "Discount")
    pdf.cell(40, 10, "Disc. Price")
    pdf.cell(30, 10, "Subtotal")
    pdf.ln()
    pdf.cell(200, 10,"--------------------------------------------------------------------------------------------------------------------------------------", ln=True, align="C")

    total_amount  =  0
    for item in order_items:
        product=db.query(Product).filter(Product.product_id  ==  item.product_id, Product.status == 1).first()
        if not product:
             return {"status": 0, "msg": "product not found"}

        product_name=product.product_name
        original_price=product.product_price
        product_discount=product.product_discount
        discount_price=original_price-(original_price*product_discount / 100)
        subtotal=discount_price * item.quantity
        total_amount += subtotal

        pdf.cell(80, 10, product_name)
        pdf.cell(20, 10, str(item.quantity))
        pdf.cell(30, 10, f"Rs.{original_price:.2f}")
        pdf.cell(30, 10, f"{product_discount}%")
        pdf.cell(40, 10, f"Rs.{discount_price:.2f}")
        pdf.cell(30, 10, f"Rs.{subtotal:.2f}")
        pdf.ln()
    pdf.cell(200, 10,"--------------------------------------------------------------------------------------------------------------------------------------", ln=True, align="C")
    tax_rate = 10
    tax_amount =(total_amount * tax_rate)  /100
    total=total_amount +  tax_amount

    pdf.cell(200, 10, f"Subtotal: Rs.{total_amount:.2f}", ln=True)
    pdf.cell(200, 10, f"Tax ({tax_rate}%): Rs.{tax_amount:.2f}", ln=True)
    pdf.cell(200, 10, f"Total: Rs.{total:.2f}", ln=True)
    pdf.cell(200, 10, "-----------------------------------------------------", ln=True, align="C")
    pdf.cell(200, 10, "    Thank you for shopping !", ln=True, align="C")
    pdf.cell(200, 10, "-----------------------------------------------------", ln=True, align="C")

    timestamp=str(datetime.timestamp(datetime.now()))
    pdf_filename=f"invoice_{order_id}_{timestamp}_.pdf"
    pdf_path= os.path.join(LOCAL_STORAGE_PATH,pdf_filename)
    pdf.output(pdf_path)

    pdf_url = pdf_path
    order.pdf_url = pdf_url
    db.commit()

    return {"status": 1, 
            "pdf_url": pdf_url}
