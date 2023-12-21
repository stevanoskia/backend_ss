from flask import Blueprint, render_template, request, jsonify, send_from_directory
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, InputRequired, Length, ValidationError, EqualTo
from flask_jwt_extended import get_jwt_identity, jwt_required
from Config.Config import app
from Routes.Products.ProductCRUD import ProductCrud
from Config.Common import crud_routes, convertor
from Models.Models import Products, Categories, Subcategories
from flask import send_from_directory

products_api = Blueprint('products', __name__)



@products_api.route('/images/<filename>')
def send_image(filename):
    return send_from_directory('/usr/share/nginx/html/static/', filename)

#ADD----------------------------------------------------
@products_api.route('/add_product', methods=['GET'])
def add_product():
    categories = Categories.query.all()
    subcategories = Subcategories.query.all()


    return render_template('add_product.html', categories = categories, subcategories = subcategories)

@products_api.route('/create_product', methods=['POST'])
def create_product():
    response = ProductCrud.create(request)
    return response


#READ----------------------------------------------------
@products_api.route('/read_products', methods=['GET'])
def read_products():
    #response = ProductCrud.read(request)
    response = crud_routes(request, ProductCrud)
    return render_template('read_products.html', product_list=response.get_json()['products'], category_list=response.get_json()['category'], subcategory_list=response.get_json()['subcategory'])
    #return crud_routes(request, ProductCrud)


#UPDATE----------------------------------------------------
@products_api.route('/update_products/<int:pid>', methods=['GET'])
def update_product(pid):
    product = Products.query.filter_by(pid=pid).first()
    if not product:
        return "Product not found", 404
    return render_template('update_products.html', product=product)

@products_api.route('/update_products', methods=['POST'])
def save_updated_product():
    response = ProductCrud.update(request)
    return response



#DELETE----------------------------------------------------
@products_api.route('/delete_product/<int:pid>', methods=['POST'])
def delete_product(pid):
    response = ProductCrud.delete(pid)
    return response



@products_api.route('/image/<filename>')
def serve_image(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


#PRODUCTS CARDS API

    #POST PRODUCTS TO ProductList
@products_api.route("/getProducts", methods=["GET", "PUT" , "POST"])
def products_crud():
    return crud_routes(request, ProductCrud)

    #POST PRODUCT DATA TO ProductDetals (Every product card by id)
@products_api.route('/product/<int:pid>', methods=["GET", "PUT" , "POST"])
def get_product_by_id(pid):
    return ProductCrud.get_product_by_id(pid)


    #POST TO Sidebar 
@products_api.route('/getCategories', methods=['GET'])
def get_categories():
    
    categories = Categories.query.all()
    ret_categories = [{"cid": category.cid, "name": category.name} for category in categories]

    return jsonify({"categories": ret_categories})

    #POST TO Sidebar 
@products_api.route('/getSub', methods=['GET'])
def get_sub():

    subcategories = Subcategories.query.all()
    ret_subcategories = [{"scid": subcategory.scid, "cid": subcategory.cid ,"name": subcategory.name} for subcategory in subcategories]

    return jsonify({"subcategories": ret_subcategories})


#POST TO Search 
@products_api.route('/searchProducts', methods=['GET'])
def searchProducts():
    products = Products.query.all()
    subcategories = Subcategories.query.all()
    categories = Categories.query.all()

    ret_products = [{"pid": product.pid, "name": product.name} for product in products]
    ret_subcategories = [{"scid": subcategory.scid, "cid": subcategory.cid ,"name": subcategory.name} for subcategory in subcategories]
    ret_categories = [{"cid": category.cid ,"name": category.name} for category in categories]

    return jsonify({"subcategories": ret_subcategories, "products": ret_products,"categories": ret_categories })
#------------------------

#PROBABLY NOT USED
@products_api.route('/get_subcategories', methods=['GET'])
def get_subcategories():
    cid = request.args.get('cid')
    if not cid:
        return jsonify({"subcategories": []})

    subcategories = Subcategories.query.filter_by(cid=cid).all()
    subcategories_list = [
        {"scid": subcategory.scid, "name": subcategory.name} for subcategory in subcategories
    ]
    return jsonify({"subcategories": subcategories_list})


@products_api.route('/getProductsBySubcategory/<int:scid>', methods=['GET'])
def get_products_by_subcategory(scid):
    products = Products.query.filter(Products.scid == scid).all()
    ret_products = convertor(products, ["password", "reset_code"], True)
    return jsonify({"products": ret_products})


# Add to cart route
@products_api.route('/cart/add', methods=['POST'])
def add_to_cart():
    data = request.json
    product_id = data.get('productId')
    # Logic to add the product to the cart (database, session, etc.)
    return jsonify({"message": "Product added to cart"})

# Get cart contents route
@products_api.route('/cart', methods=['GET'])
def get_cart_contents():
    # Logic to retrieve cart contents
    cart_contents = [...]  # Replace with actual cart data
    return jsonify({"cart": cart_contents})
