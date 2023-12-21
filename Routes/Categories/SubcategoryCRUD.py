from Models.Models import Subcategories, Categories
from Config.Config import app, db

from flask import jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, jwt_required
from Config import Constants, Common
from Config.Common import custom_abort, crud_routes, build_params, get_user_from_jwt, convertor, hash_query_results, get_hash_info, get_random_alphanumerical, get_extension

#MODEL
class Subcategory():
    def __init__(self): 
        self.table_keys = {
            "scid": "Integer",
            "name": "String",
            "info": "String",

            "cid": "Integer",

    }
        
#-----------------CRUD---------------------------
    #-----------CREATE------------------------------
    def create(self, request):
        data = request.form
        required_keys = ["name", "info", "cid"]
        for key in required_keys:
            if key not in data:
                return custom_abort(400, "Required key is missing from request - " + key)

        if Categories.query.filter_by(cid=data["cid"]).first() is None:
            return custom_abort(404, "Category with the given 'scid' not found")

        subcategory = Subcategories()
        [setattr(subcategory, key, data[key]) for key in required_keys]
        db.session.add(subcategory)
        db.session.commit()
        subcategory = Subcategories.query.filter_by(scid=subcategory.scid).first()

        ret = convertor(subcategory)

        return jsonify({
            "subcategory": ret
        })

        
    #-----------READ------------------------------

    def read(self , request):
        hash_info = get_hash_info(request.args)
        params = build_params(self.table_keys, request.args)

        subcategory = Subcategories.query.filter_by(**params).all()
        category = Categories.query.filter_by(**params).all()
        ret = convertor(subcategory, ["password", "reset_code"], True)
        ret1 = convertor(category, ["password", "reset_code"], True)
        if hash_info["enable_hash"] == True:
            ret = hash_query_results(ret, hash_info["hash_key"], hash_info["hash_type"])

        if hash_info["enable_hash"] == True:
            ret1 = hash_query_results(ret, hash_info["hash_key"], hash_info["hash_type"])

        return jsonify({"subcategory": ret, "hash_info": hash_info, "category": ret1})
    
    
    #-----------UPDATE------------------------------

    # @jwt_required()
    def update(self, request):
        data = request.form
        if "scid" not in data:
            return custom_abort(400, "Required key is missing from request - id")

        subcategory = Subcategories.query.filter_by(scid=data["scid"]).first()
        category = Categories.query.filter_by(cid=data["cid"]).first()

        if subcategory is None:
            return custom_abort(404, "Subcategory not found")

        if category is None:
            return custom_abort(404, "Category with the given 'cid' not found")

        [setattr(subcategory, key, data[key]) for key in self.table_keys if key in data]

        db.session.commit()
        ret_subcategory = convertor(subcategory)

        return jsonify({
            "subcategory" : ret_subcategory
        })
    
    #-----------DELETE------------------------------

    def delete(self, scid):
        subcategory = Subcategories.query.filter_by(scid=scid).first()

        if subcategory is None:
            return custom_abort(404, "subcategory not found")

        db.session.delete(subcategory)
        db.session.commit()

        return jsonify({
            "message": "subcategory deleted successfully"
        })

SubcategoryCrud = Subcategory()