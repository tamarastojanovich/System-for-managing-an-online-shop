from json import JSONDecodeError
from email.utils import parseaddr
from flask import Flask,Response
from flask import request,redirect
from flask import jsonify
from sqlalchemy.orm import Query
from collections import namedtuple

from flask_jwt_extended import JWTManager
from flask_jwt_extended import create_access_token
from flask_jwt_extended import create_refresh_token
from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_jwt_identity

from configuration import Configuration
import os
import subprocess
from model import database
from model import migrate
from model import Product
from model import ProductCategory
from model import Category
from model import Order
from model import OrderContainsProduct
from ownerdecorator import roleCheck
import io
import csv

application = Flask(__name__)
application.config.from_object(Configuration)
jwt = JWTManager ( application )

database.init_app(application)

    
migrate.init_app(application, database)

@application.route("/",methods=["GET"])
def fun():
    return "HELLLLLLLO"

@application.route("/update",methods=["POST"])
@roleCheck(role="owner")
def update():
    message=""
    if 'file' not in request.files:
        message+="Field file is missing."
        return jsonify({'message':message}),400
    
    productsFile=request.files["file"].stream.read().decode("utf-8")
    productsStream=io.StringIO(productsFile)
    productTable=csv.reader(productsStream)
    
    
    count=0
    producto=namedtuple("Product",["categories","name","price"])
    products=[]
    for product in productTable:
        
        price=0
        if len(product) < 3:
            message+="Incorrect number of values on line "+str(count)+"."
            return jsonify({'message':message}),400
        try:
            float(product[2])
            if float(product[2]) <= 0:
                message+="Incorrect price on line "+str(count)+"."
                return jsonify({'message':message}),400
        except:
            message+="Incorrect price on line "+str(count)+"."
            return jsonify({'message':message}),400
            
        name=product[1]
        
        
        productExists=Product.query.filter(Product.prod==name).first()
        
        if productExists:
            message+="Product "+name+" already exists."
            return jsonify({'message':message}),400
            
        products.append(producto(categories=product[0],name=product[1],price=product[2]))
        count=count+1
        
        
    for product in products:
            float(product[2])
            price=float(product[2])
       
            
        
            categories=product[0].split("|")
            name=product[1]
        
        
            productExists=Product.query.filter(Product.prod==name).first()
        
            if productExists is None:
                #znaci ne postoji dati proizvod,sada je potrebno da prodjemo kroz sve kat i vidimo sta ima i sta nema
                pro=Product(name=name,price=price)
                database.session.add(pro)
                for cat in categories:
                    catExists=Category.query.filter(Category.category==cat).first()
                    
                    if catExists is None:
                        c=Category(cat)
                        database.session.add(c)
                    
                    proCat=ProductCategory(cat=cat,prod=name)
                    database.session.add(proCat)#dodali smo odnos izmedju proizvoda i kategorije

        
    
    database.session.commit()
    return Response(status=200)
    
@application.route("/product_statistics")
@roleCheck(role="owner")
def product_stat():
    return redirect("http://127.0.0.1:9090/product_statistics")
    

@application.route("/category_statistics",methods=["GET"])
@roleCheck(role="owner")
def cat_stat():
    return redirect("http://127.0.0.1:9090/categories_statistics")

if ( __name__ == "__main__" ):
    HOST = "0.0.0.0" if ( "PRODUCTION" in os.environ ) else "127.0.0.1"
    application.run ( debug = True, host = HOST,port=5001 )