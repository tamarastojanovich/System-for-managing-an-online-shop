from flask import Flask
from flask import request
from flask import jsonify
from collections import namedtuple
from sqlalchemy import or_
from flask_jwt_extended import JWTManager
from web3 import Web3
from web3 import HTTPProvider
from web3 import exceptions

from configuration import Configuration
import os
from model import database
from model import migrate
from model import Order
from ownerdecorator import roleCheck

application = Flask(__name__)
application.config.from_object(Configuration)
jwt = JWTManager ( application )

database.init_app(application)

migrate.init_app(application, database)


def read_file ( path ):
    with open ( path, "r" ) as file:
        return file.read ( )

@application.route("/",methods=["GET"])
def fun():
    return "HELLLLLLLoooO"

@application.route("/orders_to_deliver",methods=["GET"])
@roleCheck("courier")
def orders():
    ord=database.session.query(Order).filter(Order.status=='CREATED').all()
    ord_info=namedtuple("order",['id','email'])
    ret=[]
    for o in ord:
        ret.append(ord_info(id=o.orderId,email=o.owner))
    my_dict = [dict(zip(("id", "email"), x)) for x in ret]
    return jsonify({'orders':my_dict}),200



@application.route("/pick_up_order",methods=["POST"])
@roleCheck("courier")
def pick_up():
    id=request.json.get("id",None)
    address=request.json.get("address","")
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
    if order_exists[0].status!="CREATED":
        return jsonify({'message':"Invalid order id."}),400
    if address=="":
        return jsonify({'message':"Missing address."}),400
    
    web3 = Web3 ( HTTPProvider ( "http://127.0.0.1:8545" ) )
    valid=web3.is_address(address)
    if valid==False:
        return jsonify({'message':"Invalid address."}),400
    
    order=database.session.query(Order).filter(Order.orderId==id).first() 
    addr = web3.to_checksum_address(order.address)
    bytecode=read_file ( "../solidity/output/ShopAgreement.bin" )
    abi      = read_file ( "../solidity/output/ShopAgreement.abi" )
    
    contract = web3.eth.contract ( bytecode = bytecode, abi = abi,address=addr)
    
    owner_adr="0x11595aE12cFee525C470c296FeD0552112b86665"
    owner_priv="0xb64be88dd6b89facf295f4fd0dda082efcbe95a2bb4478f5ee582b7efe88cf60"
    
    try:
        trans= contract.functions.take_order(web3.to_checksum_address(address)).build_transaction ({
        "gasPrice":21000,
        "nonce":web3.eth.get_transaction_count ( web3.to_checksum_address(owner_adr) )
        })
        
        signed_transaction = web3.eth.account.sign_transaction ( trans, owner_priv )
        transaction_hash   = web3.eth.send_raw_transaction ( signed_transaction.rawTransaction )
        receipt            = web3.eth.wait_for_transaction_receipt ( transaction_hash )

       # contract = web3.eth.contract ( address = receipt.contractAddress, abi = abi )
        
        order.status="PENDING"
        database.session.commit()
        
    except exceptions.ContractLogicError as error: 
       message=error.message.removeprefix("execution reverted: VM Exception while processing transaction: revert ")
       return jsonify({'message':message}),400
        
    
    
   
    
    return jsonify(),200


if ( __name__ == "__main__" ):
    HOST = "0.0.0.0" if ( "PRODUCTION" in os.environ ) else "127.0.0.1"
    application.run ( debug = True, host = HOST,port=5003 )
