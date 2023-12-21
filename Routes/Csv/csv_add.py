from Config.Config import app, db
from flask import Flask, request, render_template, Blueprint, jsonify
import os
from werkzeug.exceptions import BadRequest

from werkzeug.utils import secure_filename

import pandas as pd


csv_api = Blueprint('csv', __name__)

from Models.Models import Categories
from Models.Models import Subcategories
from Models.Models import Products

from Config.Common import custom_abort, crud_routes, build_params, get_user_from_jwt, convertor, hash_query_results, get_hash_info, get_random_alphanumerical, get_extension


def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}  # Define your allowed extensions here
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Category csv upload

@csv_api.route('/category_csv', methods=['POST'])
def upload_csv_category():
    try:
        # Access the uploaded CSV file using request.files
        csv_file = request.files['csvFile']

        if csv_file:
            # Read the CSV file using pandas
            csv_data = pd.read_csv(csv_file)

            # Insert data into the 'Categories' table
            for index, row in csv_data.iterrows():
                new_category = Categories(name=row['name'], info=row['info'])
                db.session.add(new_category)
            
            db.session.commit()

            return "CSV data uploaded and processed successfully."

        return "No file selected or an error occurred."

    except Exception as e:
        return str(e)


@csv_api.route('/subcategory_csv', methods=['POST'])
def upload_csv_subcategory():
    try:
        # Access the uploaded CSV file using request.files
        csv_file = request.files['csvFile']

        if csv_file:
            # Read the CSV file using pandas
            csv_data = pd.read_csv(csv_file)

            for index, row in csv_data.iterrows():
                # Check if the 'cid' value is present in the CSV file
                if 'cid' in row:
                    # Retrieve the 'cid' value from the CSV file
                    cid_value = row['cid']

                    # Query the 'Categories' table to find the associated category
                    category = Categories.query.filter_by(cid=cid_value).first()

                    if category:
                        # If the category exists, create a new subcategory and associate it with the category
                        new_subcategory = Subcategories(name=row['name'], info=row['info'], cid=category.cid)
                        db.session.add(new_subcategory)
                    else:
                        return f"Error: Category with cid={cid_value} not found in the database."

            db.session.commit()

            return "CSV data uploaded and processed successfully."

        return "No file selected or an error occurred."

    except Exception as e:
        return str(e)

@csv_api.route('/product_csv', methods=['POST'])
def upload_csv_product():
    try:
        csv_file = request.files['csvFile']
        product_gifs = request.files.getlist('product_gifs[]')
        product_images = request.files.getlist('product_images[]')
        product_images_paths = []
        product_gifs_paths = []

        if csv_file:
            # Read the CSV file using pandas
            csv_data = pd.read_csv(csv_file)

            for index, row in csv_data.iterrows():
                # Extract product data from the CSV file
                product_images_paths = []
                product_gifs_paths = []
                product_name = row['name']
                product_info = row['info']
                product_price = row['price']
                product_price_Discount = row['price_Discount']
                product_productNo = row['productNo']
                product_description = row.get('description', '')  # Handle optional field
                product_description2 = row.get('description2', '')  
                product_brand = row.get('brand', '')  # Handle optional field
                product_color = row.get('color', '')  # Handle optional field
                product_cid = row['cid']  # Assuming 'cid' is provided in the CSV
                product_scid = row['scid']  # Assuming 'scid' is provided in the CSV

                # Check for and handle image paths in the CSV
                gif_paths = row.get('product_path')
                product_paths = row.get('product_paths').split(',')  # Assuming multiple paths are comma-separated

                # Assuming 'allowed_file' and 'custom_abort' functions are defined elsewhere

                if 'product_images[]' in request.files:
                    product_images = request.files.getlist('product_images[]')
                    for product_image in product_images:
                        print("Uploaded file name:", product_image.filename)

                        if allowed_file(product_image.filename):
                            filename = secure_filename(product_image.filename)
                            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

                            if not os.path.exists(image_path):
                                print("Saving file to:", image_path)
                                product_image.save(image_path)
                            else:
                                print(f"File '{filename}' already exists in the upload folder. Skipping upload.")
                            product_images_paths.append(filename)

                        else:
                            return custom_abort(400, "Invalid file format. Allowed formats: jpg, jpeg, png, gif")

                if 'product_gifs[]' in request.files:
                    product_gifs = request.files.getlist('product_gifs[]')
                    for product_gif in product_gifs:
                        print("Uploaded file name:", product_gif.filename)

                        if allowed_file(product_gif.filename):
                            filename = secure_filename(product_gif.filename)
                            gif_filename = secure_filename(product_gif.filename)
                            gif_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

                            if not os.path.exists(gif_path):
                                print("Saving file to:", gif_path)
                                product_gif.save(gif_path)
                            else:
                                print(f"File '{filename}' already exists in the upload folder. Skipping upload.")
                            product_gifs_paths.append(filename)

                        else:
                            return custom_abort(400, "Invalid file format. Allowed formats: jpg, jpeg, png, gif")

                product_paths_str = ','.join(product_paths)
                gif_paths = ','.join(product_gifs_paths)

                # Query the 'Categories' and 'Subcategories' tables to find the associated category and subcategory
                category = Categories.query.filter_by(cid=product_cid).first()
                subcategory = Subcategories.query.filter_by(scid=product_scid).first()

                if category and subcategory:
                    # If both category and subcategory exist, create a new product
                    new_product = Products(
                        name=product_name,
                        info=product_info,
                        price=product_price,
                        price_Discount=product_price_Discount,
                        productNo=product_productNo,
                        description=product_description,
                        description2=product_description2,
                        brand=product_brand,
                        color=product_color,
                        cid=category.cid,
                        scid=subcategory.scid,
                        product_path=gif_filename,
                        product_paths=product_paths_str
                    )
                    print (product_paths)
                    db.session.add(new_product)
                else:
                    return f"Error: Category with cid={product_cid} or Subcategory with scid={product_scid} not found in the database."

            db.session.commit()

            return "CSV data uploaded and processed successfully."

        return "No file selected or an error occurred."

    except Exception as e:
        return str(e)
