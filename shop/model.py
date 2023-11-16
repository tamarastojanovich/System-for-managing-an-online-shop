from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

database = SQLAlchemy()

migrate=Migrate ()

class ProductCategory(database.Model):
    __tablename__ = "productCategory"

    id = database.Column(database.Integer, primary_key = True)
    prod = database.Column(database.String(256), database.ForeignKey("products.prod"), nullable = False)
    category = database.Column(database.String(256), database.ForeignKey("categories.category"), nullable = False)

    def __init__(self,prod,cat):
       self.prod=prod
       self.category=cat

class OrderContainsProduct(database.Model):
    __tablename__="orderPro"
    
    id=database.Column(database.Integer,primary_key=True)
    orderId=database.Column(database.Integer,database.ForeignKey("orders.orderId"),nullable=False)
    prod=database.Column(database.String(256),database.ForeignKey("products.prod"),nullable=False)
    quantity=database.Column(database.Integer,nullable=False)
    def __init__(self,ord,pro,q):
        self.orderId=ord
        self.prod=pro
        self.quantity=q
    
class Product(database.Model):
    __tablename__ = "products"

    id=database.Column(database.Integer,primary_key=True)
    prod = database.Column(database.String(256), unique=True)
    price = database.Column(database.Double, nullable=False)

    categories = database.relationship("Category", secondary = ProductCategory.__table__,back_populates = "products" )
    orders = database.relationship("Order", secondary = OrderContainsProduct.__table__,back_populates = "products" )
    def __init__(self,name,price):
        self.prod=name
        self.price=price

class Category( database.Model):
    __tablename__ = "categories"

    category = database.Column(database.String(256), primary_key=True)

    products = database.relationship("Product", secondary=ProductCategory.__table__, back_populates="categories")

    def __init__(self,name):
        self.category=name
        

class Order(database.Model):
    __tablename__ = "orders"
    
    orderId=database.Column(database.Integer,primary_key=True)
    price=database.Column(database.Double,nullable=False)
    status=database.Column(database.String(256),nullable=False)
    created=database.Column(database.String(256),nullable=False)
    owner=database.Column(database.String(256),nullable=False)
    address=database.Column(database.String(256),nullable=False)
    
    products = database.relationship("Product", secondary=OrderContainsProduct.__table__, back_populates="orders")
    
    def __init__(self,price,status,date,owner,address):
        self.price=price
        self.status=status
        self.created=date
        self.owner=owner
        self.address=address