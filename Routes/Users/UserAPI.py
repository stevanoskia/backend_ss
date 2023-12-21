from flask import Blueprint, render_template, request, jsonify,redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, InputRequired, Length, ValidationError, EqualTo
from flask import render_template_string
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, verify_jwt_in_request


from Routes.Users.UserCRUD import userCrud
from Routes.Users.UserAUTH import user_auth 

from Config.Common import crud_routes
user_api = Blueprint('index', __name__)


#ROUTES-----------------------
@user_api.route('/getUser', methods=["GET", "UPDATE"])
@jwt_required()
def getUser():
    current_user = get_jwt_identity()  # Get the user information from the JWT token
    #print(str(current_user) + "TEST")

    # Call the 'readId' function to fetch the user by their ID
    response, status_code = userCrud.readId(request,current_user)

    if status_code == 200:
        user_data = response.get_json()['user']

        return jsonify(user_data), status_code

    else:
        error_message = response
        return error_message
    #print(str(user_data) + "OVA E OVA E" + str(status_code) + "STATUS")
    #if isinstance(user_data, tuple) and user_data[1] == 200:
       # return user_data
    #else:
        # Handle the case where the user is not found or there's an error
        #return user_data



#-------------------LOGIN--------------------------------

@user_api.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        response, status_code = user_auth.login(request)
        if status_code == 200:
            user_data = response.get_json()['user']
            access_token = create_access_token(identity=user_data)
            user_data['access_token'] = access_token
            return jsonify(user_data), status_code
        else:
            error_message = response
            return error_message


@user_api.route('/register', methods=["GET", "POST"])
def register():

    if request.method == "POST":
        response, status_code = user_auth.register(request)
        if status_code == 200:
            return response,status_code #smeni pokasno

        else:
            error_message = response
            return error_message



@user_api.route('/ne', methods=["GET", "UPDATE"])
def users():
    #current_user = get_jwt_identity()  # Get the user information from the JWT token
    return render_template("index.html", flask_token="hello flask")
