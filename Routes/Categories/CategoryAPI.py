from flask import Blueprint, render_template, request, jsonify,redirect, url_for, flash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, InputRequired, Length, ValidationError, EqualTo
from flask_jwt_extended import get_jwt_identity, jwt_required

from Routes.Categories.CategoryCRUD import CategoryCrud
from Config.Common import crud_routes
from Models.Models import Categories

categories_api = Blueprint('categories', __name__)


#ADD----------------------------------------------------
@categories_api.route('/add_category', methods=['GET'])
def add_category():
    return render_template('add_category.html')

@categories_api.route('/create_category', methods=['POST'])
def create_category():
    response = CategoryCrud.create(request)
    return response


#READ----------------------------------------------------
@categories_api.route('/read_categories', methods=['GET'])
def read_categories():
    response = crud_routes(request, CategoryCrud)
    return render_template('read_categories.html', category_list=response.get_json()['category'])


#UPDATE----------------------------------------------------
@categories_api.route('/update_category/<int:cid>', methods=['GET', 'POST'])
def update_category(cid):
    category = Categories.query.filter_by(cid=cid).first()
    if not category:
        return "Category not found", 404
    return render_template('update_category.html', category=category)

@categories_api.route('/update_category', methods=['GET', 'POST'])
def save_updated_category():
    response = CategoryCrud.update(request)
    if response.status_code == 200:
        flash('Category updated successfully!', 'success')
        return redirect("https://localhost:5000/secret/read_categories")
    else:
        return response
    
#DELETE----------------------------------------------------
@categories_api.route('/delete_category/<int:cid>', methods=['GET', 'POST'])
def delete_category(cid):
    category = Categories.query.filter_by(cid=cid).first()
    if not category:
        return "Category not found", 404

    if request.method == 'POST':
        response = CategoryCrud.delete(cid)
        return response

    return render_template('delete_category.html', category=category)
