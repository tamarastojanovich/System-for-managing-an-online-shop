from functools import wraps
from flask_jwt_extended import verify_jwt_in_request, get_jwt;
from flask import Response
from jwt import PyJWT
import requests
from flask import request,jsonify

def roleCheck ( role ):
    def innerRole ( function ):
        @wraps ( function )
        def decorator ( *arguments, **keywordArguments ):
            verify_jwt_in_request ( )
           # r=requests.get(request.base_url)
           # jwtt=r.headers["Authorization"]
            header=request.headers.get('Authorization')
            if header is None:
                return jsonify({'msg':"Missing Authorization Header"}),401 
            token=header.split()[1]
            claims = PyJWT().decode(jwt=token,key="JWT_SECRET_DEV_KEY",algorithms=["HS256"])
            if role==claims["roles"] :
                return function ( *arguments, **keywordArguments )
            else:
                return jsonify({'msg':"Missing Authorization Header"}),401 

        return decorator

    return innerRole
