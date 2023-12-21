from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_jwt_extended import get_jwt_identity, jwt_required
from werkzeug.security import check_password_hash

from Routes.Products.ProductCRUD import ProductCrud
from Routes.Categories.CategoryCRUD import CategoryCrud
from Routes.Categories.SubcategoryCRUD import SubcategoryCrud

from Config.Common import crud_routes, convertor
from Models.Models import Products, Categories, Subcategories, Auth

admin_api = Blueprint('Auth', __name__)

from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

from Config.Config import app, db, login_manager
from Routes.Users.UserCRUD import userCrud


#MODEL
class AuthConfig():
    def __init__(self): 
        self.table_keys = {
            "id": "Integer",
            "username": "String",
            "password": "String",
    }
    

@login_manager.user_loader
def load_user(user_id):
    return Auth.query.get(int(user_id))



@admin_api.route('/adminAuth', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        print("Attempting login with username:", username)
        
        admin = Auth.query.filter_by(username=username).first()

        if admin and admin.password == password:  # Compare passwords without hashing
            print("Login successful for user:", username)
            login_user(admin)
            return redirect('/secret/read_products')  # Use direct URL path

        print("Invalid login attempt for user:", username)
        flash('Invalid username or password', 'danger')

    return render_template('adminAuth.html')

@admin_api.route('/logoutAdmin', methods=['GET'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('/api/secret/adminAuth'))  # Change 'auth.login' to 'Auth.login'



@admin_api.route('/read_users', methods=["GET", "UPDATE"])
@login_required
def sendUsers():
    response = crud_routes(request, userCrud)
    user_list = response.get_json()['user'] 
    return render_template('read_users.html', user_list=user_list)






#ADD----------------------------------------------------
@admin_api.route('/add_product', methods=['GET'])
@login_required
def add_product():
    categories = Categories.query.all()
    subcategories = Subcategories.query.all()

    subcategories_data = {}
    for subcategory in subcategories:
        if subcategory.cid not in subcategories_data:
            subcategories_data[subcategory.cid] = []
        subcategories_data[subcategory.cid].append({
            'scid': subcategory.scid,
            'name': subcategory.name
        })

    return render_template('add_product.html', categories = categories, subcategories = subcategories_data)

@admin_api.route('/create_product', methods=['POST'])
@login_required
def create_product():
    response = ProductCrud.create(request)
    return response


#READ----------------------------------------------------
@admin_api.route('/read_products', methods=['GET'])
@login_required
def read_products():
    #response = ProductCrud.read(request)
    response = crud_routes(request, ProductCrud)
    return render_template('read_products.html', product_list=response.get_json()['products'], category_list=response.get_json()['category'], subcategory_list=response.get_json()['subcategory'])
    #return crud_routes(request, ProductCrud)


#UPDATE----------------------------------------------------
@admin_api.route('/update_products/<int:pid>', methods=['GET'])
@login_required
def update_product(pid):
    product = Products.query.filter_by(pid=pid).first()
    categories = Categories.query.all()
    subcategories = Subcategories.query.all()   
    print(product.product_path)
    if not product:
        return "Product not found", 404
    
    subcategories_data = {}
    for subcategory in subcategories:
        if subcategory.cid not in subcategories_data:
            subcategories_data[subcategory.cid] = []
        subcategories_data[subcategory.cid].append({
            'scid': subcategory.scid,
            'name': subcategory.name
        })
    return render_template('update_products.html', product=product, categories=categories, subcategories=subcategories_data)

@admin_api.route('/update_products', methods=['POST'])
@login_required
def save_updated_product():
    response = ProductCrud.update(request)
    return response

#DELETE----------------------------------------------------
@admin_api.route('/delete_product/<int:pid>', methods=['POST'])
def delete_product(pid):
    response = ProductCrud.delete(pid)
    return response


#------------SUBCATEGORIES--------------------------------
#ADD----------------------------------------------------
@admin_api.route('/add_subcategory', methods=['GET'])
@login_required
def add_subcategory():
    categories = Categories.query.all()
    return render_template('add_subcategory.html', categories = categories)

@admin_api.route('/create_subcategory', methods=['POST'])
@login_required
def create_subcategory():
    response = SubcategoryCrud.create(request)
    return response


#READ----------------------------------------------------
@admin_api.route('/read_subcategories', methods=['GET'])
@login_required
def read_subcategories():
    response = crud_routes(request, SubcategoryCrud)
    return render_template('read_subcategories.html', subcategory_list=response.get_json()['subcategory'], category_list=response.get_json()['category'])



#UPDATE----------------------------------------------------
@admin_api.route('/update_subcategory/<int:scid>', methods=['GET', 'POST'])
@login_required
def update_subcategory(scid):
    subcategory = Subcategories.query.filter_by(scid=scid).first()
    category_list = Categories.query.all()

    if not subcategory:
        return "Subcategory not found", 404

    return render_template('update_subcategory.html', subcategory=subcategory, category_list=category_list)

@admin_api.route('/update_subcategory', methods=['GET', 'POST'])
@login_required
def save_updated_subcategory():
    response = SubcategoryCrud.update(request)

    if response.status_code == 200 :
        flash('Subcategory updated successfully!', 'success')
        return redirect(url_for('subcategories.read_subcategories'))
    else:
        return response
    
#DELETE----------------------------------------------------
@admin_api.route('/delete_subcategory/<int:scid>', methods=['GET', 'POST'])
@login_required
def delete_subcategory(scid):
    subcategory = Subcategories.query.filter_by(scid=scid).first()
    if not subcategory:
        return "Subcategory not found", 404

    if request.method == 'POST':
        response = SubcategoryCrud.delete(scid)
        return response

    return render_template('delete_subcategory.html', subcategory=subcategory)



#-------------------CATEGORIES--------------------------


#ADD----------------------------------------------------
@admin_api.route('/add_category', methods=['GET'])
@login_required
def add_category():
    return render_template('add_category.html')

@admin_api.route('/create_category', methods=['POST'])
@login_required
def create_category():
    response = CategoryCrud.create(request)
    return response


#READ----------------------------------------------------
@admin_api.route('/read_categories', methods=['GET'])
@login_required
def read_categories():
    response = crud_routes(request, CategoryCrud)
    return render_template('read_categories.html', category_list=response.get_json()['category'])


#UPDATE----------------------------------------------------
@admin_api.route('/update_category/<int:cid>', methods=['GET', 'POST'])
@login_required
def update_category(cid):
    category = Categories.query.filter_by(cid=cid).first()
    if not category:
        return "Category not found", 404
    return render_template('update_category.html', category=category)

@admin_api.route('/update_category', methods=['GET', 'POST'])
@login_required
def save_updated_category():
    response = CategoryCrud.update(request)
    if response.status_code == 200:
        return redirect(url_for('categories.read_categories'))
    else:
        return response
    
#DELETE----------------------------------------------------
@admin_api.route('/delete_category/<int:cid>', methods=['GET', 'POST'])
@login_required
def delete_category(cid):
    category = Categories.query.filter_by(cid=cid).first()
    if not category:
        return "Category not found", 404

    if request.method == 'POST':
        response = CategoryCrud.delete(cid)
        return response

    return render_template('delete_category.html', category=category)
