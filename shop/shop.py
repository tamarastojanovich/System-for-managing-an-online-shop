from json import JSONDecodeError
from email.utils import parseaddr
from flask import Flask
from flask import request,Response
from flask import jsonify
from sqlalchemy.orm import Query
from collections import namedtuple
from sqlalchemy import and_
from datetime import datetime,timezone
import json
from collections import OrderedDict
from web3 import Web3
from web3 import HTTPProvider
from web3 import Account
from web3 import exceptions
from cryptography.exceptions import InvalidSignature


from flask_jwt_extended import JWTManager
from flask_jwt_extended import create_access_token
from flask_jwt_extended import create_refresh_token
from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import get_jwt

from configuration import Configuration
import os
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

owner_priv="0xb64be88dd6b89facf295f4fd0dda082efcbe95a2bb4478f5ee582b7efe88cf60"
def read_file ( path ):
    with open ( path, "r" ) as file:
        return file.read ( )

@application.route("/",methods=["GET"])
def fun():
    return "HELLLLLLLO"


@application.route("/search",methods=["GET"])
@roleCheck("customer")
def search():
    name=request.args.get('name',"")
    categories=request.args.get("category","")
    
    name_search="%{}%".format(name)
    #first_filter=ProductCategory.query.filter(ProductCategory.prod.like(name_search))#dohv sve proizvode koji odg
    
    categories_search="%{}%".format(categories)
    second_filter=ProductCategory.query.filter(and_(ProductCategory.prod.like(name_search),ProductCategory.category.like(categories_search)))
    
    cat_set=set()
    prod_set=set()
    
    for pc in second_filter:
        cat_set.add(pc.category)
        prod_set.add(pc.prod)
    
    cat_list=[]
    for c in cat_set:
        cat_list.append(c)
        
    #sada je potrebno napisati za proizvode sve
    products=[]
    prod_info=namedtuple("products",["categories","id","name","price"])
    for p in prod_set:
        
        info=database.session.query(Product.id,Product.prod,Product.price,ProductCategory.category).select_from(Product).filter(Product.prod==p).join(ProductCategory,ProductCategory.prod==Product.prod).all()
        price=info[0].price
        id=info[0].id
        #jos kategorije
        cat=[]
        for i in info:
            cat.append(i.category)
       
        products.append(prod_info(cat,id,p,price))
    my_dict = [OrderedDict(zip(("categories", "id","name","price"), x)) for x in products]
    return jsonify({"categories":cat_list,"products":my_dict}),200

@application.route("/order",methods=["POST"])
@roleCheck("customer")
def order():
    claims = get_jwt ( )
    owner=claims["email"]
    requests=request.json.get("requests",None)
    address=request.json.get("address","")
    if requests is None:
        return jsonify({'message':"Field requests is missing."}),400
     
    message=""
    element=1
    price=0
    products=[]
    quantities=[]
    for r in requests:
        id=0
        q=0
        if "id" not in r:
            element=0
            break
        else:
            id=r["id"]
        if "quantity" not in r:
            element=0
            break
        else:
            q=r["quantity"]
        if not isinstance(id,int) or id<=0:
            element=0
            break
        if not isinstance(q,int) or q<=0:
            element=0
            break
        product=database.session.query(Product).filter(Product.id==id).first()
        
        if product is None:
            element=0
            break
    
    for r in requests:
        error=0
        id=0
        q=0
        if "id" not in r:
            message+="Product id is missing for request number " + str(element) +"."
            return jsonify({'message':message}),400
            error=1
        else:
            id=r["id"]
        if "quantity" not in r:
            message+="Product quantity is missing for request number " + str(element) +"."
            return jsonify({'message':message}),400
            error=1
        else:
            q=r["quantity"]
        if not isinstance(id,int) or id<=0:
             message+="Invalid product id for request number " + str(element) +"."
             return jsonify({'message':message}),400
             error=1
        if not isinstance(q,int) or q<=0:
            message+="Invalid product quantity for request number " + str(element) +"."
            return jsonify({'message':message}),400
            error=1    
        product=database.session.query(Product).filter(Product.id==id).first()
        
        if product is None:
            message+="Invalid product for request number "+str(element)+"."
            return jsonify({'message':message}),400
            element=element+1
            continue
        price=price+q*product.price
        
        if(product.prod in products):
            ind=products.index(product.prod)
            quantities[ind]=quantities[ind]+q
        else:
            products.append(product.prod)#napravim listu i onda na osnovu indeksa paralelnih znam kolicinu
            quantities.append(q)
        element=element+1
    if len(message)>0:
        return jsonify({'message':message}),400
    if len(address)==0:
        return jsonify({'message':"Field address is missing."}),400
    
    web33 = Web3 ( HTTPProvider ( "http://127.0.0.1:8545" ) )
    valid=web33.is_address(address)
    if valid==False:
        return jsonify({'message':"Invalid address."}),400
    
    bytecode = read_file ( "../solidity/output/ShopAgreement.bin" )
    abi      = read_file ( "../solidity/output/ShopAgreement.abi" )

    contract = web33.eth.contract ( bytecode = bytecode, abi = abi )
    
    owner_adr="0x11595aE12cFee525C470c296FeD0552112b86665"
    
    
    result = web33.eth.send_transaction ({
    "from": web33.eth.accounts[2],
    "to": owner_adr,
    "value": web33.to_wei ( 2, "ether" )
})
    
    customer_account = web33.to_checksum_address(str(address))
    #customer_account=Account.from_key(str(address).split("0x")[1])
    owner_addr=web33.to_checksum_address(owner_adr)
    transaction = contract.constructor ( int(price), customer_account,owner_addr ).build_transaction ({
    "gasPrice":21000,
    "nonce":web33.eth.get_transaction_count ( owner_addr)
    })

    signed_transaction = web33.eth.account.sign_transaction ( transaction, owner_priv )
    transaction_hash   = web33.eth.send_raw_transaction ( signed_transaction.rawTransaction )
    receipt            = web33.eth.wait_for_transaction_receipt ( transaction_hash )

    contract = web33.eth.contract ( address = receipt.contractAddress, abi = abi )
    
    ord=Order(price=price,status="CREATED",date=str(datetime.now().isoformat()),owner=owner,address=contract.address)
    
    database.session.add(ord)
    database.session.commit()
    for i in range(0,len(products)):
        pro_ord=OrderContainsProduct(ord=ord.orderId,pro=products[i],q=quantities[i])
        database.session.add(pro_ord)
        database.session.commit()
    return jsonify({"id":ord.orderId}),200

@application.route("/status",methods=["GET"])
@roleCheck("customer")
def stat():
    claims=get_jwt()
    id=claims["email"]
    orders=database.session.query(Order).filter(Order.owner==id)
    ord=[]
    ord_tuple=namedtuple("Order",['products','price','status','timestamp'])
    for o in orders:
        pro=[]
        products=database.session.query(OrderContainsProduct).filter(OrderContainsProduct.orderId==o.orderId).all()
        #svi proizvodi za dati order
        prod=namedtuple("prod",['categories','name','price','quantity'])
        for p in products:
            info_pro=database.session.query(Product).filter(Product.prod==p.prod).all()
            cat=database.session.query(ProductCategory).filter(ProductCategory.prod==p.prod).all()
            cat_list=[]
            for c in cat:
                cat_list.append(c.category)
            pro.append(prod(categories=cat_list,name=p.prod,price=info_pro[0].price,quantity=p.quantity))
        dicti=[OrderedDict(zip(("categories", "name","price","quantity"), x)) for x in pro]
        ord.append(ord_tuple(products=dicti,price=o.price,status=o.status,timestamp=o.created))
    my_dict = [OrderedDict(zip(("products", "price","status","timestamp"), x)) for x in ord]
    return jsonify({'orders':my_dict}),200

@application.route("/delivered",methods=["POST"])
@roleCheck("customer")
def delivered():
    #claims=get_jwt()-+
    id=request.json.get("id",None)
    if id is None:
        return jsonify({'message':"Missing order id."}),400
    try:
        int(id)
        if int(id) <= 0:
            return jsonify({'message':"Invalid order id."}),400
    except:
        return jsonify({'message':"Invalid order id."}),400
    order_exists=database.session.query(Order).filter(Order.orderId==id).all()
    if len(order_exists)==0:
        return jsonify({'message':"Invalid order id."}),400
    if order_exists[0].status!="PENDING":
        return jsonify({'message':"Invalid order id."}),400
    
    
    keys=request.json.get("keys",None)
    if keys is None:
        return jsonify({'message':"Missing keys."}),400
    if len(keys)==0:
        return jsonify({'message':"Missing keys."}),400
    #keys=json.loads(keys)
    passphrase=request.json.get("passphrase","")
    if len(passphrase)==0:
        return jsonify({'message':"Missing passphrase."}),400
    
    
    web3 = Web3 ( HTTPProvider ( "http://127.0.0.1:8545" ) )
    
    try:
        keys=json.loads(keys)
    except json.decoder.JSONDecodeError:
        return jsonify({'message':"Invalid customer account."}),400
    
    
    try:
        priv_key=Account.decrypt(json.dumps(keys),passphrase)
        
    except ValueError:
        return jsonify({'message':"Invalid credentials."}),400
    
    
    
    
    priv_key=priv_key.hex()
    addr=Account.from_key(priv_key).address
    right_keys=web3.to_checksum_address ( keys["address"] )
    if(addr!=right_keys):
         return jsonify({'message':"Invalid credentials."}),400

    order=database.session.query(Order).filter(Order.orderId==id).first()
    
    
    
    address = web3.to_checksum_address(order.address)
    bytecode=read_file ( "../solidity/output/ShopAgreement.bin" )
    abi      = read_file ( "../solidity/output/ShopAgreement.abi" )
    
    contract = web3.eth.contract ( bytecode = bytecode, abi = abi,address=address )
    
    
    owner_adr="0x11595aE12cFee525C470c296FeD0552112b86665"
    
    try:
        trans=contract.functions.confirm(web3.to_checksum_address(addr)).build_transaction({
            "gasPrice":21000,
            "nonce":web3.eth.get_transaction_count(web3.to_checksum_address(addr))
            })
        
        signed_transaction = web3.eth.account.sign_transaction ( trans, priv_key )
        transaction_hash   = web3.eth.send_raw_transaction ( signed_transaction.rawTransaction )
        receipt            = web3.eth.wait_for_transaction_receipt ( transaction_hash )
        
        
        order.status="COMPLETE"
        database.session.commit()
    
    except exceptions.ContractLogicError as error:
       message=error.message.removeprefix("execution reverted: VM Exception while processing transaction: revert ")
       return jsonify({'message':message}),400
    
    
    #web3.sendTransaction({"to":owner_adr, "from":addr, "value":int(order.price)})
    
    
    return Response(status=200)

@application.route("/pay",methods=["POST"])
@roleCheck("customer")
def pay():
    owner_adr="0x11595aE12cFee525C470c296FeD0552112b86665"
    id=request.json.get("id",None)
    if id is None:
        return jsonify({'message':"Missing order id."}),400
    try:
        int(id)
        if int(id) <= 0:
            return jsonify({'message':"Invalid order id."}),400
    except:
        return jsonify({'message':"Invalid order id."}),400
    
    order=database.session.query(Order).filter(Order.orderId==id).first()
    if order is None :
        return jsonify({'message':"Invalid order id."}),400
    
    keys=request.json.get("keys",None)
    if keys is None:
        return jsonify({'message':"Missing keys."}),400
    if len(keys)==0:
        return jsonify({'message':"Missing keys."}),400
    
    #keys=json.loads(keys)
    passphrase=request.json.get("passphrase","")
    if len(passphrase)==0:
        return jsonify({'message':"Missing passphrase."}),400
    
    
    
    web3 = Web3 ( HTTPProvider ( "http://127.0.0.1:8545" ) )
    
    try:
        keys=json.loads(keys)
    except json.decoder.JSONDecodeError:
        return jsonify({'message':"Invalid customer account."}),400
    
    
    try:
        priv_key=Account.decrypt(json.dumps(keys),passphrase)
        
    except ValueError:
        return jsonify({'message':"Invalid credentials."}),400
    
    
    
    
    priv_key=priv_key.hex()
    addr=Account.from_key(priv_key).address
    right_keys=web3.to_checksum_address ( keys["address"] )
    if(addr!=right_keys):
         return jsonify({'message':"Invalid credentials."}),400

    address = web3.to_checksum_address(order.address)
    bytecode=read_file ( "../solidity/output/ShopAgreement.bin" )
    abi      = read_file ( "../solidity/output/ShopAgreement.abi" )
    
    contract = web3.eth.contract ( bytecode = bytecode, abi = abi,address=address )
    
    balance=web3.eth.get_balance(addr)
    if balance<order.price:
        return jsonify({'message':"Insufficient funds."}),400
    
    price=order.price
    
    try:
        trans=contract.functions.pay(web3.to_checksum_address(addr)).build_transaction({
            "chainId":web3.eth.chain_id,
            "from": web3.to_checksum_address(addr),
            "nonce":web3.eth.get_transaction_count ( web3.to_checksum_address(addr)),
            "value": int(price),
            "gasPrice":21000
        })
        
        signed_transaction = web3.eth.account.sign_transaction ( trans, priv_key )
        transaction_hash   = web3.eth.send_raw_transaction ( signed_transaction.rawTransaction )
        receipt            = web3.eth.wait_for_transaction_receipt ( transaction_hash )
        #contract=web3.eth.contract(address=receipt.contractAddress,abi=abi)
        #order.address=contract.address
        #database.session.commit()
        
        
    except exceptions.ContractLogicError as error:
       message=error.message.removeprefix("execution reverted: VM Exception while processing transaction: revert ")
       return jsonify({'message':message}),400
   
   
    return Response(status=200)
   
if ( __name__ == "__main__" ):
    HOST = "0.0.0.0" if ( "PRODUCTION" in os.environ ) else "127.0.0.1"
    application.run ( debug = True, host = HOST,port=5002 )