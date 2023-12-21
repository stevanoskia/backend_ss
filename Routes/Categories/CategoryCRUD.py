from Models.Models import Categories
from Config.Config import app, db

from flask import jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, jwt_required
from Config import Constants, Common
from Config.Common import custom_abort, crud_routes, build_params, get_user_from_jwt, convertor, hash_query_results, get_hash_info, get_random_alphanumerical, get_extension

#MODEL
class Category():
    def __init__(self): 
        self.table_keys = {
            "cid": "Integer",
            "name": "String",
            "info": "String",
    }
        
#-----------------CRUD---------------------------
    #-----------CREATE------------------------------
    def create(self , request):
        data = request.form
        print(data)
        # print(data["type_id"])
        required_keys = ["name","info"]
        for key in required_keys:
            if key not in data:
                return custom_abort(400, "Недостасува компулсивен клуч - " + key)
                
            category = Categories() 
            #event = Events(banner_photo = "")
            [setattr(category, key, data[key]) for key in required_keys]
            db.session.add(category)
            db.session.commit()
            category = Categories.query.filter_by(cid=category.cid).first()

            ret = convertor(category)

            return jsonify({
                "category" : ret
            })
        
    #-----------READ------------------------------

    def read(self , request):
        hash_info = get_hash_info(request.args)
        params = build_params(self.table_keys, request.args)
        
        category = Categories.query.filter_by(**params).all()
        ret = convertor(category, ["password", "reset_code"], True)

        if hash_info["enable_hash"] == True:
            ret = hash_query_results(ret, hash_info["hash_key"], hash_info["hash_type"])

        return jsonify({ "category" : ret, "hash_info" : hash_info }) 
    
    
    #-----------UPDATE------------------------------

    # @jwt_required()
    def update(self , request):
        data = request.form
        if "cid" not in data:
            return custom_abort(400, "Required key is missing from request - id")
        # identity = get_jwt_identity()
        # auth_user = get_user_from_jwt(identity)
        # if auth_user.id != data["organizer_id"]:
        #     return custom_abort(403, "Forbidden")
        # if auth_user.type_id < 2:
        #     return custom_abort(401, "You are not authorized to update users.")
        category = Categories.query.filter_by(cid=data["cid"]).first()

        if category is None:
            return custom_abort(404, "category not found")
            
        [setattr(category, key, data[key]) for key in self.table_keys if key in data]
        db.session.commit()
        category = Categories.query.filter_by(cid=category.cid).first()
        ret = convertor(category)
        return jsonify({
            "category" : ret
        })
    
    #-----------DELETE------------------------------

    def delete(self, cid):
        category = Categories.query.filter_by(cid=cid).first()

        if category is None:
            return custom_abort(404, "category not found")

        db.session.delete(category)
        db.session.commit()

        return jsonify({
            "message": "category deleted successfully"
        })

CategoryCrud = Category()