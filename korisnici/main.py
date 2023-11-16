from json import JSONDecodeError
from email.utils import parseaddr
from flask import Flask
from flask import request,Response
from flask import jsonify
from sqlalchemy.orm import Query
from flask_jwt_extended import JWTManager
from flask_jwt_extended import create_access_token
from flask_jwt_extended import create_refresh_token
from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import get_jwt
import re
from jwt import PyJWT
import base64
import json
from configuration import Configuration

from models import database
from models import migrate
from models import User
from models import Role
import datetime
from models import UserRole

application = Flask(__name__)
application.config.from_object(Configuration)

database.init_app(application)

migrate.init_app(application, database)



regex = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')

def isValid(email):
    if re.fullmatch(regex, email):
      return True
    else:
      return False

@application.route("/",methods=["GET"])
def hello():
    return "HELLO"


@application.route("/register_customer", methods=["POST"])
def registerCustomer():
    message = ""
    # provera da li su date sve info ili nesto nedostaje
    forename = request.json.get("forename","")
    if len(forename) == 0:
        message = "Field forename is missing."
        return jsonify({'message':message}),400
    surname = request.json.get("surname","")
    if len(surname) == 0:
        message = "Field surname is missing."
        return jsonify({'message':message}),400
    email = request.json.get("email","")
    if len(email) == 0:
        message = "Field email is missing."
        return jsonify({'message':message}),400
    password = request.json.get("password","")
    if len(password) == 0:
        message = "Field password is missing."
        return jsonify({'message':message}),400
    ret = isValid(email)

    if ret == False:
        message="Invalid email."
        return jsonify({'message':message}),400
    if len(password) < 8:
        message = "Invalid password."
        return jsonify({'message':message}),400
    

    userExists=User.query.filter(User.email == email).first ()

    if(userExists is not None):
        return jsonify({'message':'Email already exists.'}),400

    new_customer = User(
        forename=forename,
        surname=surname,
        email=email,
        password=password
    )

    database.session.add(new_customer)
    database.session.commit()


    roleExists = Role.query.filter(Role.name == "customer").first()

    user_role = UserRole(user=new_customer.id, role=roleExists.id )

    database.session.add(user_role)
    database.session.commit()

    return jsonify({'message':"Successful registration."}),200


@application.route("/register_courier", methods=["POST"])
def registerCourier():
    message = ""
    # provera da li su date sve info ili nesto nedostaje
    forename = request.json.get("forename","")
    if len(forename) == 0:
        message = "Field forename is missing."
        return jsonify({'message':message}),400
    surname = request.json.get("surname","")
    if len(surname) == 0:
        message = "Field surname is missing."
        return jsonify({'message':message}),400
    email = request.json.get("email","")
    if len(email) == 0:
        message = "Field email is missing."
        return jsonify({'message':message}),400
    password = request.json.get("password","")
    if len(password) == 0:
        message = "Field password is missing."
        return jsonify({'message':message}),400
    ret = isValid(email)

    if ret == False:
        message="Invalid email."
        return jsonify({'message':message}),400
    if len(password) < 8:
        message = "Invalid password."
        return jsonify({'message':message}),400
    

    userExists = User.query.filter(User.email == email).first()

    if (userExists is not None):
        return jsonify({'message': 'Email already exists.'}),400

    new_courier = User(
        forename=forename,
        surname=surname,
        email=email,
        password=password
    )

    database.session.add(new_courier)
    database.session.commit()

    role = "courier"

    roleExists = Role.query.filter(Role.name == role).first()

    user_role = UserRole(user=new_courier.id, role=roleExists.id)

    database.session.add(user_role)
    database.session.commit()

    return Response(status=200)


jwt = JWTManager(application)
@application.route("/login",methods=["POST"])
def login ():
    message = ""
    email=""
    email = request.json.get("email","")
    if len(email)==0:
        message = "Field email is missing."
           # return Response(message,status=400)
        return jsonify({'message':message}),400
    password = request.json.get("password","")
    if len(password) == 0:
        message = "Field password is missing."
            #return Response(message,status=400)
        return jsonify({'message':message}),400
    
    ret = isValid(email)

    if ret == False:
        message = "Invalid email."
        #return Response(message,status=400)
        return jsonify({'message':message}),400

    #user = User.query.filter(User.email == email, User.password == password).first ()
    user=database.session.query(User).filter(User.email == email, User.password == password).first()
    role=""
    if user is None:
        message = "Invalid credentials."
        #return Response(message,status=400)
        return jsonify({'message':message}),400
    else:
        get_role=database.session.query(Role).join(UserRole,UserRole.roleId==Role.id).where(UserRole.userId==user.id).all()
        role=get_role[0].name


    
    #accessToken = create_access_token(identity=email,additional_claims= claims)
    claims = {
        'sub': email,
        'forename': user.forename,
        'surname': user.surname,
        'email':email,
        'password':user.password,
        'roles': role,
        'type':'access',
        'exp':datetime.datetime.utcnow()+datetime.timedelta(hours=1),
        'nbf':datetime.datetime.utcnow(),
        'iat':datetime.datetime.utcnow()
        }
    
    access=PyJWT().encode(payload=claims,key=application.config["JWT_SECRET_KEY"],algorithm='HS256')
    
    return jsonify({'accessToken':access}),200

@application.route("/delete",methods=["POST"])
@jwt_required()
def delete():
    iden = get_jwt_identity()
    #OVDE DODATI PROVERU ZA IDEN
    if iden is None:
         #return Response('Unknown user.',status=400)
         return jsonify({'message': 'Unknown user.'}),400
     
    user = User.query.filter(User.email == iden).first ()
    if user  is None:
       # return Response('Unknown user.',status=400)
        return jsonify({'message': 'Unknown user.'}),400
    userRole = UserRole.query.filter(UserRole.userId==user.id).first()

    database.session.delete(userRole)
    database.session.commit()
    
    database.session.delete(user)
    database.session.commit()

    return jsonify({'message':'deleted'})

import os
if ( __name__ == "__main__" ):
    HOST = "0.0.0.0" if ( "PRODUCTION" in os.environ ) else "127.0.0.1"
    application.run ( debug = True, host = HOST,port=5000 )
