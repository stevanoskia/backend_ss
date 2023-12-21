from Models.Models import Users
from Config.Config import app, db

from flask import jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, jwt_required
from Config import Constants, Common
from Config.Common import custom_abort, crud_routes, build_params, get_user_from_jwt, convertor, hash_query_results, get_hash_info, get_random_alphanumerical, get_extension

#MODEL
class User():
    def __init__(self):
        self.table_keys = {
            "uid": "Integer",
            "first_name": "String",
            "last_name": "String",
            "phone_number": "String",
            "address": "String",
            "address_number": "String",
            "email": "String",
            "password": "String",
            "profile_path": "String",
        }
    

    #USERS

    #-----------------READ
    user = Users()


    
    
    def readd(self, request):
        params = build_params(self.table_keys, request.args)
        user = Users.query.filter_by(**params).all()
       
        #user = Users.query.all()
        ret = convertor(user)

        return ret
        #return jsonify({
        #    "User" : ret
        #})
        
    #

    def readId(self, request, user_id):
        try:
            # Extract the 'uid' attribute from the 'user_id' object
            uid = user_id.get('uid')
            print("-----------" + str(uid))
            if uid is not None:
                user = Users.query.get(uid)
                print(user)
                if user is not None:
                    ret = convertor(user, ["password", "reset_code"], True)
                    return jsonify({"user": ret}), 200
                else:
                    return jsonify({"message": "User not found"}), 404
            else:
                return jsonify({"message": "Invalid user ID"}), 400
        except Exception as e:
            # Log the exception for debugging purposes
            print(f"Error in readId: {str(e)}")
            return jsonify({"message": "Internal Server Error"}), 500

    
    def read(self, request):
        hash_info = get_hash_info(request.args)
        params = build_params(self.table_keys, request.args)
        
        user = Users.query.filter_by(**params).all()
        ret = convertor(user, ["password", "reset_code"], True)

        if hash_info["enable_hash"] == True:
           ret = hash_query_results(ret, hash_info["hash_key"], hash_info["hash_type"])

        return jsonify({ "user" : ret, "hash_info" : hash_info }) 

    @jwt_required()
    def update(self, request):
        data = request.form
        files = request.files
        if "uid" not in data:
            return custom_abort(400, "Required key is missing from request - id")

        identity = get_jwt_identity()
        auth_user = get_user_from_jwt(identity)
        user = Users.query.filter_by(uid = data["uid"]).first()
        if user is None:
            return custom_abort(404, "User not found")

        #if (auth_user.type_id == 1 and auth_user.id != user.id) or (auth_user.type_id < user.type_id):
#return custom_abort(401, "You are not authorized to update users.")

        if "email" in data:
            exists_email = Users.query.filter_by(email = data["email"]).first()
            if exists_email is not None or exists_email.id != user.id:
                return custom_abort(409, "This email address is already in use.")

        #if "phone_number" in data:
        #    exists_phone = Users.query.filter_by(phone_number = data["phone_number"]).first()
       #     if exists_phone is not None or exists_phone.id != user.id:
       #         return custom_abort(409, "This phone number is already in use.")

        #if "profile_path" in files:
         #   profile_picture = files["profile_path"]
          #  relative_path = "/users/" + get_random_alphanumerical() + "." + get_extension(profile_picture)
           # profile_picture.save(constants["static_root"] + relative_path)
            #user.profile_path = relative_path


        [setattr(user, key, data[key]) for key in self.table_keys if key in data]
        db.session.commit()
        user = Users.query.filter_by(uid = data["uid"]).first()
        ret = convertor(user, ["password", "reset_code"])

        return jsonify({"user" : ret})

    def delete(self, request):
        pass



    #

userCrud = User()