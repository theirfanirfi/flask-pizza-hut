from flask import Flask, render_template, request, redirect, url_for, flash
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import update
from flask_migrate import Migrate
from flask_login import LoginManager, login_required, current_user, login_user, logout_user
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
import os
from flask_mail import Mail, Message



# Configure Flask app
app = Flask(__name__)


app.config["MAIL_SERVER"] = 'smtp.gmail.com'
app.config["MAIL_PORT"] = 465
app.config["MAIL_USE_TLS"] = False
app.config["MAIL_USE_SSL"] = True
app.config["MAIL_USERNAME"] = os.getenv('EMAIL_USER')
app.config["MAIL_PASSWORD"] = os.getenv('EMAIL_PASSWORD')
mail = Mail(app)

# DB_URL = 'postgres://ciptcygpfsoale:309ad767947bfc6a6f678f0822987bfe16d58da95c8ae044a51ef96697f0f559@ec2-50-17-21-170.compute-1.amazonaws.com:5432/da5h46n7mk9mdc'
# Configure database
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# Configure session, use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")


Session(app)

db = SQLAlchemy(app)
from models import *


# Configure migrations
Migrate(app, db)

login_manager = LoginManager()

login_manager.login_view = '/login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class AdminModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.role == "admin"
    def inaccessible_callback(self, name, **kwargs):
        return redirect("/login")
    form_excluded_columns = ['cart','menuitems']


admin = Admin(app,name='Pinocchio Admin')
admin.add_view(AdminModelView(User, db.session))
admin.add_view(AdminModelView(Menu, db.session))
admin.add_view(AdminModelView(MenuItems, db.session))
admin.add_view(AdminModelView(Cart, db.session, "Orders"))


@app.route("/")
@login_required
def index():
    menu = Menu.query.join(MenuItems).all()
    return render_template('index.html', menu=menu)


# @app.route("/toppers")
# @login_required
# def toppers():
#     menu = Menu.query.filter_by(is_topping=True).join(MenuItems).all()
#     return render_template('toppers.html', menu=menu)


@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == "GET":
        return render_template('login.html')
    elif request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if not user:
            flash('Invalid Credentials', 'danger')
            return redirect("/login")
        if user.check_password(password) and user is not None:
            login_user(user)
            if user.role == "admin":
                return redirect('/admin')
            else:
                return redirect('/')
        else:
            flash('Invalid Credentials', 'danger')
            return redirect("/login")
    else:
        return redirect("/login")

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == "GET":
        return render_template('registeration.html')
    elif request.method == "POST":
        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if not user:
            u = User(username=username,firstname=firstname,lastname=lastname,email=email,password=password,role="customer")
            try:
                db.session.add(u)
                db.session.commit()
                flash('Registeration successfull. You are logged in now','success')
                login_user(u)
                return redirect("/")
            except Exception as e:
                flash('Error occurred. please try again. '+str(e),'danger')
                return redirect("/register")
        else:
            flash('Email is already in use. Please user another one.', 'danger')
            return redirect("/register")
    else:
        return redirect("/regiseration.html")

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/login")

@app.route('/addtocart',methods=['POST'])
@login_required
def add_to_cart():
    user = current_user
    items = request.form.getlist('items')
    total_price = request.form.get('total_price')
    has_toppings = False
    if not (len(items) >0):
        flash('Select items first','danger')
        return redirect(request.referrer)

    for item in items:
        mitem = MenuItems.query.filter_by(id=item).first()
        if not mitem:
            flash('Invalid item added to cart','danger')
            return redirect(request.referrer)

        cart = Cart(item_id=item,user_id=user.id,menu_id=mitem.menu_id)
        try:
            db.session.add(cart)
            db.session.commit()
            menu = Menu.query.filter_by(id=mitem.menu_id).first()
            if menu.has_toppings:
                has_toppings = True
        except Exception as e:
            flash('Error: '+str(e),'danger')
            return redirect(request.referrer)

    if has_toppings:
        menu = Menu.query.filter_by(is_topping=True).join(MenuItems).all()
        return render_template('toppers.html',tprice=total_price, menu=menu)
    else:
        flash('Items added to cart, you can checkout now.','success')
        return redirect("/cart")


@app.route('/cart')
@login_required
def cart():
    user = current_user
    cart = Cart.query.join(MenuItems, (MenuItems.id == Cart.item_id)).filter(Cart.user_id == user.id, Cart.checkout == 'Not confirmed').all()
    total_price = 0
    total_items = 0
    for c in cart:
        total_items +=1
        total_price += c.menu_items.price

    return render_template('cart.html',cart=cart, total_price=total_price, total_items=total_items)

@app.route('/sendemail')
@login_required
def send_email():
    user = current_user
    cart = Cart.query.join(MenuItems, (MenuItems.id == Cart.item_id)).filter(Cart.user_id == user.id, Cart.checkout == 'Not confirmed').all()
    total_price = 0
    total_items = 0
    for c in cart:
        total_items +=1
        total_price += c.menu_items.price

    msg = Message(subject="Pizza Hut Oder Confirmation",sender=str(os.getenv('EMAIL_USER')),recipients=[user.email], body="Pizza hut order")
    msg.html = render_template('email_confirmation_cart.html', cart=cart, total_price=total_price, total_items=total_items)
    mail.send(msg)
    flash('Confirmation email is sent to your email, please confirm','success')
    return redirect("/")


@app.route('/confirm')
@login_required
def confirm_order():
    user = current_user
    try:
        db.session.query(Cart).filter(Cart.checkout == 'Not confirmed', Cart.user_id == user.id).update(
            {Cart.checkout: 'confirmed'})
        db.session.commit()
        flash('Order confirmed','success')
        return redirect("/")
    except Exception as e:
        return 'not confirmed '+str(e)


@app.route('/myorders')
@login_required
def my_orders():
    user = current_user
    cart = Cart.query.filter(Cart.user_id==user.id, Cart.checkout=='confirmed').all()
    return render_template('myorders.html',cart=cart)

if __name__ == "__main__":
    app.run(debug=True)
