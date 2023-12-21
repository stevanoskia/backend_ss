from flask import jsonify
#from Config.Config import db, uri
from Models.Models import Users
from sqlalchemy.orm import sessionmaker, scoped_session
import sqlalchemy, random, datetime

def get_user_from_jwt(jwt_content):
    user = Users.query.filter_by(id = int(jwt_content["id"])).first()
    return user

def get_hash_info(args):
    return {
        "enable_hash" : False if "enable_hash" not in args or args["enable_hash"] != "true" else True,
        "hash_key" : "id" if "hash_key" not in args else args["hash_key"],
        "hash_type" : True if "hash_type" not in args or args["hash_type"] == "cbht" else False
    }

def build_params(keys, args):
    params = dict()
    for key in keys:
        if key in ["password", "reset_code"]:
            continue
        if key in args:
            params[key] = args[key] if keys[key] != "Integer" else int(args[key])
    return params

def str_to_date(str, format="%Y-%m-%d %H:%M:%S"):
    example = datetime.datetime(2021, 6, 2, 9, 39)
    if str == None: 
        return False
    
    if type(str) == type(example):
        return str
    
    return datetime.datetime.strptime(str, format)

def dict_is_xor(_dict, keys):
    exists = False
    for key in keys:
        if key in _dict and exists == False:
            exists = key
            continue
        if key in _dict and exists != False:
            return False
    
    return exists

def crud_routes(request, instance):
    method = request.method
    if method == "POST":
        return instance.create(request)
    elif method == "GET":
        return instance.read(request)
    elif method == "PUT":
        return instance.update(request)
    elif method == "DELETE":
        return instance.delete(request)

def custom_abort(code, message):
    return jsonify({
        "msg": message,
        "code" : code
    }), code
    
    translated = InterfaceTranslations.query.filter_by(interface_id=interface.id, language_id=language_id).first()
    if translated is None:
        return jsonify({
            "msg": message + append,
            "code" : code
        }), code
    
    return jsonify({
        "msg": translated.content + append,
        "code" : code
    }), code

def convertor(instance, exclude=[], force_array=False):
    if instance is None:
        return instance
    if type(instance) != list:
        instance = [instance]
        
    ret = []
    for i in instance:
        obj = dict()
        for key in i.__dict__:
            if key not in exclude and key != "_sa_instance_state":
                obj[key] = i.__dict__[key]
        ret.append(obj)
        
    if len(ret) == 1 and force_array == False:
        return ret[0]
    return ret

def hash_query_results(array, col_key, cbht=True, _dict=False):
    if type(array) != list:
        array = [array]
    if len(array) == 0:
        return []
    if _dict == False:
        ret = [None for _ in range(max(array,key=lambda x: x[col_key])[col_key]+1)]
    else:
        ret = {}
    for item in array:
        if cbht:
            ret[item[col_key]] = item
        else:
            if item[col_key] not in ret or ret[item[col_key]] is None:
                ret[item[col_key]] = [item]
            else:    
                ret[item[col_key]].append(item)
    return ret
    
def get_random_alphanumerical(_len = 16):
    asciiCodes = []
    alphanumerical = ""
    asciiCodes += random.sample(range(97, 122), int(round(0.375 * _len)))
    asciiCodes += random.sample(range(65, 90), int(round(0.375 * _len)))
    asciiCodes += random.sample(range(48, 57), int(round(0.25 * _len)))
    random.shuffle(asciiCodes)
    for char in asciiCodes:
        alphanumerical += chr(char)
    return alphanumerical

def generate_secret_key(length):
    key = ""
    for x in range(length):
        rand = random.randint(97, 122)
        key += chr(rand)
    return key

def get_extension(_f):
    ext = str(_f.filename.split(".")[len(_f.filename.split(".")) - 1])
    return ext

def conv_arg(arg):
    if arg == "null":
        return None
    else:
        return arg

class SQL:
    def __init__(self):
        self.engine = sqlalchemy.create_engine(uri, pool_recycle=1800)
        self.Session = scoped_session(sessionmaker(bind=self.engine))
        pass

    def query(self, query, params, keys):
        session = self.Session()
        result = session.execute(query, params).fetchall()
        ret = []
        for row in result:
            res = {}
            for idx, item in enumerate(row):
                res[keys[idx]] = item
            ret.append(res)

        return ret
