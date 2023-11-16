from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


database = SQLAlchemy()

migrate=Migrate ()

class UserRole(database.Model):
    __tablename__ = "userRole"

    id = database.Column(database.Integer, primary_key = True)
    userId = database.Column(database.Integer, database.ForeignKey("users.id"), nullable = False)
    roleId = database.Column(database.Integer, database.ForeignKey("roles.id"), nullable = False)

    def __init__(self,user,role):
        self.userId = user
        self.roleId = role

class User(database.Model):
    __tablename__ = "users"

    id = database.Column(database.Integer, primary_key = True)
    email = database.Column(database.String(256), nullable=False, unique=True)
    password = database.Column(database.String(256), nullable=False)
    forename = database.Column(database.String(256), nullable=False)
    surname = database.Column(database.String(256), nullable=False)

    roles = database.relationship("Role", secondary = UserRole.__table__,back_populates = "users" )
    def __init__(self,email,password,forename,surname):
        self.email=email
        self.password=password
        self.forename=forename
        self.surname=surname

class Role( database.Model):
    __tablename__ = "roles"

    id = database.Column(database.Integer, primary_key = True)
    name = database.Column(database.String(256), nullable= False)

    users = database.relationship("User", secondary=UserRole.__table__, back_populates="roles")

    def __init__(self,name):
        self.name=name

