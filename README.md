# Thermal Printer API

This project implements a FastAPI-based API for printing receipts and order details using a thermal printer.

## Features

- Print receipts with order details
- Print separate print orders
- Secure API endpoints with OAuth2 authentication
- Support for line items, addons, and discount codes

## Setup

1. Install the required dependencies:
   ```
   pip install fastapi uvicorn python-escpos prettytable
   ```

2. Configure the printer IP address in the `app.py` file.

3. Run the server:
   ```
   python app.py
   ```

## API Endpoints

### POST /print_order

```
curl -X POST "http://localhost:8000/print_order" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"order_number": "123456", "customer_name": "John Doe", "order_date": "2024-01-01", "line_items": [{"qty": 2, "product": "Product A", "price": 10.00}, {"qty": 1, "product": "Product B", "price": 15.00}], "addons": [{"name": "Addon 1", "price": 2.00}, {"name": "Addon 2", "price": 3.00}], "discount_code": "DISCOUNT10"}'
```
JSON Body
``` 
{
    "order_number": "123456",
    "customer_name": "John Doe",
    "order_date": "2024-01-01",
    "line_items": [{"qty": 2, "product": "Product A", "price": 10.00}, {"qty": 1, "product": "Product B", "price": 15.00}],
    "addons": [{"name": "Addon 1", "price": 2.00}, {"name": "Addon 2", "price": 3.00}],
    "discount_code": "DISCOUNT10"
}
```

Prints a receipt and a print order for the given order details.

#### Request Body
