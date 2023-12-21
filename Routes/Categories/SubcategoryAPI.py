from flask import Blueprint, render_template,flash, request, jsonify,redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, InputRequired, Length, ValidationError, EqualTo
from flask_jwt_extended import get_jwt_identity, jwt_required

from Routes.Categories.SubcategoryCRUD import SubcategoryCrud
from Config.Common import crud_routes
from Models.Models import Subcategories, Categories

subcategories_api = Blueprint('subcategories', __name__)


#ADD----------------------------------------------------
@subcategories_api.route('/add_subcategory', methods=['GET'])
def add_subcategory():
    categories = Categories.query.all()
    return render_template('add_subcategory.html', categories = categories)

@subcategories_api.route('/create_subcategory', methods=['POST'])
def create_subcategory():
    response = SubcategoryCrud.create(request)
    return response


#READ----------------------------------------------------
@subcategories_api.route('/read_subcategories', methods=['GET'])
def read_subcategories():
    response = crud_routes(request, SubcategoryCrud)
    return render_template('read_subcategories.html', subcategory_list=response.get_json()['subcategory'], category_list=response.get_json()['category'])



#UPDATE----------------------------------------------------
@subcategories_api.route('/update_subcategory/<int:scid>', methods=['GET', 'POST'])
def update_subcategory(scid):
    subcategory = Subcategories.query.filter_by(scid=scid).first()
    category_list = Categories.query.all()

    if not subcategory:
        return "Subcategory not found", 404

    return render_template('update_subcategory.html', subcategory=subcategory, category_list=category_list)

@subcategories_api.route('/update_subcategory', methods=['GET', 'POST'])
def save_updated_subcategory():
    response = SubcategoryCrud.update(request)

    if response.status_code == 200 :
        flash('Subcategory updated successfully!', 'success')
        return redirect("https://shopex.mk/api/secret/read_subcategories")
    else:
        return response
    
#DELETE----------------------------------------------------
@subcategories_api.route('/delete_subcategory/<int:scid>', methods=['GET', 'POST'])
def delete_subcategory(scid):
    subcategory = Subcategories.query.filter_by(scid=scid).first()
    if not subcategory:
        return "Subcategory not found", 404

    if request.method == 'POST':
        response = SubcategoryCrud.delete(scid)
        return response

    return render_template('delete_subcategory.html', subcategory=subcategory)
