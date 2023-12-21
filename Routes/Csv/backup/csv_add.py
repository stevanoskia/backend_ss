from flask import Flask, request, render_template, Blueprint, jsonify
from Config.Config import app, db
import os
import shutil
from werkzeug.utils import secure_filename
import requests

import pandas as pd

csv_api = Blueprint('csv', __name__)

from Models.Models import Categories
from Models.Models import Subcategories
from Models.Models import Products

        

def allowed_file(self, filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in self.ALLOWED_EXTENSIONS

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







# Product csv upload

@csv_api.route('/product_csv', methods=['POST'])
def upload_csv_product():
    try:
        # Access the uploaded CSV file using request.files
        csv_file = request.files['csvFile']
        source_folder = ''
        if csv_file:
            # Read the CSV file using pandas
            csv_data = pd.read_csv(csv_file)

            for index, row in csv_data.iterrows():
                # Extract product data from the CSV file
                product_name = row['name']
                product_info = row['info']
                product_price = row['price']
                product_productNo = row['productNo']
                product_description = row.get('description', '')  # Handle optional field
                product_brand = row.get('brand', '')  # Handle optional field
                product_color = row.get('color', '')  # Handle optional field
                product_cid = row['cid']  # Assuming 'cid' is provided in the CSV
                product_scid = row['scid']  # Assuming 'scid' is provided in the CSV

                # Check for and handle image paths in the CSV
                product_path = row.get('product_path', '')
                product_paths = row.get('product_paths', '')  # Assuming multiple paths are comma-separated


                #product_img = product_path.filename
                #print(product_img)
                uploaded_image_paths = []
                if product_path:
                    source_folder = request.form['sourceFolder']

                    uploaded_image_paths.append(upload_image(product_path,source_folder))
                    print(product_path + "-pp")
                if product_paths:
                    multiple_paths = product_paths.split(',')
                    source_folder = request.form['sourceFolder']
                    print(multiple_paths[0] + "-multiple_paths")
                    uploaded_image_paths.extend([upload_image(path, source_folder) for path in multiple_paths])
                    print(uploaded_image_paths[0] + "-uploaded_image_paths")



                # Query the 'Categories' and 'Subcategories' tables to find the associated category and subcategory
                category = Categories.query.filter_by(cid=product_cid).first()
                subcategory = Subcategories.query.filter_by(scid=product_scid).first()

                if category and subcategory:
                    # If both category and subcategory exist, create a new product
                    new_product = Products(
                        name=product_name,
                        info=product_info,
                        price=product_price,
                        productNo=product_productNo,
                        description=product_description,
                        brand=product_brand,
                        color=product_color,
                        cid=category.cid,
                        scid=subcategory.scid,
                        product_path=product_path,
                        product_paths=product_paths
                    )
                    db.session.add(new_product)
                else:
                    return f"Error: Category with cid={product_cid} or Subcategory with scid={product_scid} not found in the database."

            db.session.commit()

            return "CSV data uploaded and processed successfully."

        return "No file selected or an error occurred."

    except Exception as e:
        return str(e)


def upload_image(image_filename, source_folder):
    # Handle image uploads here
    # Define the destination folder for saving the image
    upload_folder = app.config['UPLOAD_FOLDER']

    # Ensure the destination folder exists; create it if it doesn't
    os.makedirs(upload_folder, exist_ok=True)

    # Generate a secure filename for the image
    filename = secure_filename(image_filename)

    # Combine the source folder and filename to get the full source path
    source_path = os.path.join(source_folder, filename)
    for f in os.listdir(source_folder):
        print(f)
    # Combine the destination folder and filename to get the full path for saving
    destination_path = os.path.join(upload_folder, filename)

    # Save the image from the source folder to the destination folder
    # Add your code to copy the image from source to destination
    #source_path.save(destination_path)
    #shutil.copy(source_path, destination_path)
    try:
        response = requests.get(source_path)
        if response.status_code == 200:
            with open(destination_path, 'wb') as f:
                f.write(response.content)
        else:
            return f"Failed to download image from {source_path}"

    except Exception as e:
        return f"Error downloading image: {str(e)}"

    return destination_path  # Return the full path where the image is saved
