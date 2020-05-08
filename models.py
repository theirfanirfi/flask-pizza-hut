from application import db
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, current_user

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128))
    firstname = db.Column(db.String(128))
    lastname = db.Column(db.String(128))
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(150), nullable=False, default="customer")  # customer | admin
    #menus = db.relationship('Menu', backref="user", lazy='dynamic')
    cart = db.relationship('Cart', backref="user", lazy='dynamic')

    def __repr__(self):
        return f"{self.firstname}"

    def __init__(self, username, firstname, lastname, email, password, role):
        self.username = username
        self.firstname = firstname
        self.lastname = lastname
        self.email = email
        # self.password = generate_password_hash(password)
        self.password = password
        self.role = role

    def check_password(self, passw):
        return self.password == passw

class Menu(db.Model):
    __tablename__ = 'menu'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    menuitems = db.relationship('MenuItems', backref="menu", lazy='dynamic')
    cart = db.relationship('Cart', backref="menu", lazy='dynamic')

    def __repr__(self):
        return f"{self.title}"



class MenuItems(db.Model):
    __tablename__ = 'menu_items'
    id = db.Column(db.Integer, primary_key=True)
    item_title = db.Column(db.String(128))
    price = db.Column(db.Integer)
    small_size = db.Column(db.String(20),default=0)
    large_size = db.Column(db.String(20),default=0)
    menu_id = db.Column(db.Integer, db.ForeignKey('menu.id'))
    cart = db.relationship('Cart', backref="menu_items", lazy='dynamic')

    def __repr__(self):
        return f"{self.item_title}"

class Cart(db.Model):
    __tablename = 'cart'
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer,db.ForeignKey('menu_items.id'), default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), default=0)
    menu_id = db.Column(db.Integer, db.ForeignKey('menu.id'), default=0)
    checkout = db.Column(db.String(40), default="Not confirmed")

    def __init__(self,item_id,user_id,menu_id):
        self.item_id = item_id
        self.user_id = user_id
        self.menu_id = menu_id

