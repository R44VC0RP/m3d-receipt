from prettytable import PrettyTable
from escpos.printer import Network
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from typing import List, Optional
import uvicorn

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class LineItem(BaseModel):
    qty: int
    product: str
    price: float

class Addon(BaseModel):
    name: str
    price: float

class Order(BaseModel):
    order_number: str
    customer_name: str
    order_date: str
    line_items: List[LineItem]
    addons: Optional[List[Addon]]
    discount_code: Optional[str]

def verify_token(token: str = Depends(oauth2_scheme)):
    # In a real application, you would verify the token here
    if token == "3bd25f6d-009d-4ebd-9a38-90417ca0682d":
        return token    
    raise HTTPException(status_code=401, detail="Invalid token")
    

@app.post("/print_order")
async def print_order(order: Order, token: str = Depends(verify_token)):
    # Initialize printer
    printer = Network("10.100.10.215")  # Printer IP Address
    printer_width = 42

    # Call your existing print functions here
    print_receipt(printer, order.dict(), printer_width)
    print_printorder(printer, order.dict(), printer_width)

    return {"message": "Order printed successfully"}

# Example 1: Simple Layout
def print_table(printer, order, printer_width):
    table = PrettyTable()
    table.field_names = ["Qty", "Product", "Price", "Total"]
    table.align["Product"] = "l"  # Left-align the Product column
    table.align["Price"] = "r"    # Right-align the Price column
    table.align["Total"] = "r"    # Right-align the Total column
    paper_width = 48
    # Calculate the width for each column
    # Calculate how many 'A' characters can fit across the paper
    char_width = paper_width // 2  # Assuming each 'A' is about 2 units wide

    # Calculate the width for each column
    qty_width = 3  # Assuming max 3 digits for quantity
    price_width = 8  # Assuming max 8 digits for price (including decimal and dollar sign)
    total_width = 8  # Assuming max 8 digits for total (including decimal and dollar sign)
    product_width = 21
    print(f"product_width: {product_width}")

    table.max_width["Qty"] = qty_width
    table.max_width["Product"] = product_width
    table.max_width["Price"] = price_width
    table.max_width["Total"] = total_width
    line_items = order["line_items"]
    subtotal = 0
    for item in line_items:
        qty = str(item['qty']).ljust(qty_width)
        product = item['product'][:product_width].ljust(product_width)
        price = f"${item['price']:.2f}".rjust(price_width)
        total = f"${item['qty'] * item['price']:.2f}".rjust(total_width)
        subtotal += item['qty'] * item['price']
        table.add_row([qty, product, price, total])
    
    printer.set(align='center')
    printer.text(table.get_string(border=False, padding_width=1) + "\n")
    
    # Print subtotal
    printer.set(align='right')
    printer.text(f"Subtotal: ${subtotal:.2f}\n\n")

    addons = order["addons"]
    
    # Print addons
    price_width = 8
    if addons:
        for addon in addons:
            addon_name = addon['name']
            addon_price = f"${addon['price']:.2f}".rjust(price_width)
            printer.text(f"{addon_name} | {addon_price}\n")
            subtotal += addon['price']
    # Print total
    printer.text("\n")
    printer.set(align='right')
    printer.text(f"Total: ${subtotal:.2f}\n\n")

    # Print total items
    printer.set(align='left')
    total_items = sum(item['qty'] for item in line_items)
    printer.text(f"Total Items: {total_items}\n")

# Example 2: Centered Header
def print_receipt(printer, order, printer_width):
    printer.set(align='center')
    #printer.text("PACKING SLIP for Order #" + order["order_number"] + "\n\n")
    printer.image("logo.png")
    printer.text("\n")
    printer.text("Mandarin 3D Prints\n")
    printer.text("mandarin3d.com\n\n")
    printer.text("Order #" + order["order_number"] + "\n")
    printer.set(align='left')
    printer.text("Customer: " + order["customer_name"] + "\n")
    printer.text("Date: " + order["order_date"] + "\n\n")
    print_table(printer, order, printer_width)
    printer.text("\n\n")
    printer.set(align='center')
    printer.text("Thank you for your order!\n")
    printer.text("--------------------------------\n")
    printer.qr("https://reviews.mandarin3d.com", size=12, center=True)
    printer.text("If you like your order, please leave us a review by scanning the QR code above.\n\nIf you have any questions, please contact us at:\n")
    printer.text("Mandarin 3D Prints\n")
    printer.text("mandarin3d.com\n")
    printer.text("info@mandarin3d.com\n")
    printer.text("(904) 386-9755\n\n")
    if order.get("discount_code"):
        printer.text("Congrats! You have a discount code for your next order. \n")
        discount_code = order["discount_code"]
        box_width = len(discount_code) + 4  # 2 spaces on each side
        printer.text("-" * box_width + "\n")
        printer.text(f"| {discount_code} |\n")
        printer.text("-" * box_width + "\n")
        

        
    printer.cut()

def print_printorder(printer, order, printer_width):
    printer.set(align='center')
    printer.text("PRINT ORDER for Order #" + order["order_number"] + "\n\n")
    printer.set(align='left')
    printer.text("Customer: " + order["customer_name"] + "\n")
    printer.text("Date: " + order["order_date"] + "\n\n")
    
    for item in order["line_items"]:
        product = item["product"]
        price = f"${item['price']:.2f}"
        padding = printer_width - len(product) - len(price)
        printer.text(f"{product}{' ' * padding}{price}\n")
        for i in range(int(item["qty"])):
            printer.text("  * " + item["product"] + "\n")
        printer.text("\n")

    printer.cut()

order = {
    "order_number": "877A2A13-0023",
    "customer_name": "Tony Crouch",
    "order_date": "2024-09-07",
    "line_items": [
        {"qty": 20, "product": "VHSLIFE All-In-One Cleaner", "price": 30.00},
        {"qty": 10, "product": "VHS to Life - Betamax Pair (2x)", "price": 1.30},
        {"qty": 20, "product": "VHS to Life - 8MM", "price": 0.52}
    ],
    "addons": [
        {"name": "Sales Tax - 7.5%", "price": 46.75},
        {"name": "Shipping", "price": 4.56}
    ],
    "discount_code": "10OFF"
}

if __name__ == "__main__":
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
