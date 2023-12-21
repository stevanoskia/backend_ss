from flask import Blueprint, Flask, request, jsonify
from flask_redmail import RedMail
from Config.Config import app
import traceback

from Routes.Products.ProductCRUD import ProductCrud

order_api = Blueprint('order', __name__)

redmail = RedMail(app)

@order_api.route('/order', methods=["POST"])
def process_order():
    try:
        data = request.json

        print(data)
        shipping_info = data.get('shippingInfo')
        products = data.get('products')  # Use 'products' key to access the array of products

        products_in_cart = []
        for product_item in products:
            product_id = product_item['productId']
            product_quantity = product_item['quantity']
            product_response = ProductCrud.get_product_by_id(product_id)  # Get the JSON response

            if 'products' in product_response.json:
                product_data = product_response.json['products']
                product_data['quantity'] = product_quantity  # Add the 'quantity' field to the product data
                products_in_cart.append(product_data)
            else:
                return jsonify({'error': 'Product not found'}), 404

        # Extract fields from shipping_info
        firstName = shipping_info.get('firstName')
        lastName = shipping_info.get('lastName')
        street = shipping_info.get('street')
        houseNumber = shipping_info.get('houseNumber')

        # Process the order data as needed
        # You can also send an email confirmation to the user

        if not firstName or not lastName:
            return jsonify({'error': 'Missing required fields'}), 400

        subject = f'New Contact Form Submission from {firstName}'
        
        email_html = f"<h1>{subject}</h1>"
        email_html += f"<p>Shipping Information:</p>"
        email_html += f"<p>First Name: {shipping_info['firstName']}</p>"
        email_html += f"<p>Last Name: {shipping_info['lastName']}</p>"
        email_html += f"<p>Street: {shipping_info['street']}</p>"
        email_html += f"<p>House Number: {shipping_info['houseNumber']}</p>"
        # Include more shipping information fields as needed

        email_html += f"<p>Products:</p>"
        for product in products_in_cart:
            email_html += f"<p>Product: {product['name']}</p>"
            email_html += f"<p>Description: {product['description']}</p>"
            email_html += f"<p>Price: ${product['price']}</p>"
            email_html += f"<p>Quantity: {product['quantity']}</p>"
    # Include more product details as needed

        # Using redmail.send to send the email
        redmail.send(
            subject=subject,
            receivers=['nikoloski.davorr@gmail.com'],
            html=email_html,
            sender='pyFlaskDBTest@hotmail.com'
        )

        return jsonify({'message': 'Email sent successfully'}), 200

    except Exception as e:
        traceback.print_exc()  # Print the full traceback
        return jsonify({'error': str(e)}), 500
