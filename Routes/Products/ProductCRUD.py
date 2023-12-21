from Models.Models import Products, Categories, Subcategories
from Config.Config import app, db
from werkzeug.utils import secure_filename
import os
from flask import jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, jwt_required
from Config import Constants, Common
from Config.Common import custom_abort, crud_routes, build_params, get_user_from_jwt, convertor, hash_query_results, get_hash_info

#MODEL
class Product():

    ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}

    def __init__(self): 
        self.table_keys = {
            "pid": "Integer",
            "name": "String",
            "info": "String",
            "description": "String",
            "description2": "String",
            "brand": "String",
            "color": "String",
            "price": "Integer",
            "price_Discount": "Integer",
            "productNo": "String",
            "product_path": "String",
            "product_paths": "String",
            "available": "Boolean", 
            "cid": "Integer",
            "scid": "Integer",
    }
        
#-----------------CRUD---------------------------
    #-----------CREATE------------------------------
    
    
    def allowed_file(self, filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in self.ALLOWED_EXTENSIONS

    

    def create(self , request):
        data = request.form
        print(data)
        product_path = None
        product_paths = []

        # MULTIPLE IMAGES
        if 'product_images[]' in request.files:
            product_images = request.files.getlist('product_images[]')
            print(product_images[0])
            for product_image in product_images:
                print("Uploaded file name:", product_image.filename)

                if self.allowed_file(product_image.filename):
                    filename = secure_filename(product_image.filename)
                    image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

                    if not os.path.exists(image_path):
                        print("Saving file to:", image_path)
                        product_image.save(image_path)
                        product_paths.append(filename)
                    else:
                        print(f"File '{filename}' already exists in the upload folder. Skipping upload.")
                        product_paths.append(filename)

                else:
                    return custom_abort(400, "Invalid file format. Allowed formats: jpg, jpeg, png, gif")

        #------------------------------_ONE IMAGE
        
        if 'product_path' in request.files:
            product_image = request.files['product_path']

            print("Uploaded file name:", product_image.filename)

            if self.allowed_file(product_image.filename):
                filename = secure_filename(product_image.filename)
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

                if not os.path.exists(image_path):
                    print("Saving file to:", image_path)
                    product_image.save(image_path)
                    product_path = filename
                else:
                    print(f"File '{filename}' already exists in the upload folder. Skipping upload.")
                    product_path = filename

            else:
                return custom_abort(400, "Invalid file format. Allowed formats: jpg, jpeg, png, gif")

        
        product_paths_str = ','.join(product_paths)
        price_discount = request.form.get('price_Discount', None)

        # Set a default value of 0 if "price_Discount" is not provided
        if price_discount is None:
            price_discount = 0

        required_keys = ["name", "info", "price", "productNo", "cid", "scid", "price_Discount"]
        for key in required_keys:
            if key not in data:
                return custom_abort(400, "Required key is missing - " + key + "-----")
        
        secondary_keys = ["description","description2", "brand", "color","available"]

        for u_key in secondary_keys:
            if u_key not in data:
                return print("Недостасува : " + u_key)


        product = Products()
        [setattr(product, key, data[key]) for key in required_keys]
        [setattr(product, u_key, data[u_key]) for u_key in secondary_keys]

        product.product_path = product_path #PRIVREMENO VAKA TREBA DA BIDI URL
        product.product_paths = product_paths_str
        if 'available' in data:
            available = data['available']  # Convert to lowercase
            if available == '1':
                product.available = 1
            elif available == '0':
                product.available = 0
            else:
                # Handle invalid input (if needed)
                return custom_abort(400, "Invalid value for 'available' field")
        db.session.add(product)
        db.session.commit()
        product = Products.query.filter_by(pid=product.pid).first()

        ret = convertor(product)

        return jsonify({"product": ret})

    
    #-----------READ------------------------------

    def read(self , request):
        hash_info = get_hash_info(request.args)
        params = build_params(self.table_keys, request.args)
        
        product = Products.query.filter_by(**params).all()
        category = Categories.query.filter_by(**params).all()
        subcategory = Subcategories.query.filter_by(**params).all()


        ret_product = convertor(product, ["password", "reset_code"], True)
        ret_category = convertor(category, ["password", "reset_code"], True)
        ret_subcategory = convertor(subcategory, ["password", "reset_code"], True)

        if hash_info["enable_hash"] == True:
            ret_product = hash_query_results(ret_product, hash_info["hash_key"], hash_info["hash_type"])
       
        return jsonify({ "products" : ret_product,"category" : ret_category, "subcategory" : ret_subcategory,"hash_info" : hash_info }) 
    
    
    #-----------UPDATE------------------------------

    def update(self, request):
        data = request.form
        product_path = None
        product_paths = []
        product_images = []

        product_path = request.files.get('product_path')
        product_images = request.files.getlist('product_images[]')

        if "pid" not in data:
            return custom_abort(400, "Required key is missing from the request - pid")

        for product_image in product_images:
            if product_image.filename:
                print(product_image.filename + 'product_image.filename')
                if self.allowed_file(product_image.filename):
                    filename = secure_filename(product_image.filename)
                    image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

                    if not os.path.exists(image_path):
                        print("Saving file to:", image_path)
                        product_image.save(image_path)
                    else:
                        print(f"File '{filename}' already exists in the upload folder. Skipping upload.")

                    # Always add filename to product_paths list
                    product_paths.append(filename)
                else:
                    return custom_abort(400, "Invalid file format. Allowed formats: jpg, jpeg, png, gif multiple")

        product = Products.query.filter_by(pid=data["pid"]).first()

        if product is None:
                    return custom_abort(404, "Product not found")
        
        for product_image in product_images:
            if product_image.filename:
                # Join new paths if there are new images
                product_paths_str = ','.join(product_paths)
                product.product_paths = product_paths_str


        if 'product_path' in request.files:
            product_image = request.files['product_path']
            if product_image.filename:
                print(product_image.filename + 'kraen product_path')
                if self.allowed_file(product_image.filename):
                    filename = secure_filename(product_image.filename)
                    image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

                    if not os.path.exists(image_path):
                        print("Saving file to:", image_path)
                        product_image.save(image_path)
                        product.product_path = filename
                    else:
                        print(f"File '{filename}' already exists in the upload folder. Skipping upload.")
                        # Still update product object with the filename
                        product.product_path = filename
                else:
                    return custom_abort(400, "Invalid file format. Allowed formats: jpg, jpeg, png, gif")


        [setattr(product, key, data[key]) for key in self.table_keys if key in data]
        if 'available' in data:
            available = data['available']  # Convert to lowercase
            if available == '1':
                product.available = 1
            elif available == '0':
                product.available = 0
            else:
                # Handle invalid input (if needed)
                return custom_abort(400, "Invalid value for 'available' field")
        db.session.commit()
        product = Products.query.filter_by(pid=product.pid).first()
        ret = convertor(product)

        return jsonify({
            "product": ret
        })


    
    #-----------DELETE------------------------------

    def delete(self, pid):
        product = Products.query.filter_by(pid=pid).first()

        if product is None:
            return custom_abort(404, "Product not found")

        db.session.delete(product)
        db.session.commit()

        return jsonify({
            "message": "Product deleted successfully"
        })
    
    def get_product_by_id(self, pid):
        products = Products.query.filter_by(pid=pid).first()
        print(products)
        if products is None:
            return custom_abort(404, "Product not found")

        ret = convertor(products)
        return jsonify({"products": ret})

ProductCrud = Product()
