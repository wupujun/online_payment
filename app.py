#from app import app
import sys
from flask import Flask
import uuid
from flask import request
from flask import render_template, request, redirect
import stripe

app = Flask(__name__)



app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
stripe.api_key = "sk_test_E19W9fqq2f3tnvzTYtACnYD2"

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy(app)
class Product(db.Model):
    __tablename__ = 'product'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    file_name = db.Column(db.String)
    version = db.Column(db.String)
    is_active = db.Column(db.Boolean, default=True)
    price = db.Column(db.Float)
    
    def __init__(self, name, price):
        self.name = name
        self.price = price
        file_name=name
        version="1.0"


    def __repr__(self):
        return '<Product Name %r>' % self.name

class Purchase(db.Model):
    __tablename__ = 'purchase'
    uuid = db.Column(db.String, primary_key=True)
    email = db.Column(db.String)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    product = db.relationship(Product)
    downloads_left = db.Column(db.Integer, default=5)
   



@app.route('/')
def index():
    products = Product.query.all()
    return render_template("index.html", products=products)


@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404

@app.route('/buy/<ID>') 
def buy(ID):
    product= Product.query.filter_by(id=ID).first()
    return render_template("buy.html", product=product) 

@app.route('/delete/<ID>') 
def delete(ID):
    product= Product.query.filter_by(id=ID).first()
    
    db.session.delete(product)
    db.session.commit()

    products = Product.query.all()
    return render_template("index.html", products=products) 

@app.route('/add', methods=['POST'])
def add():
    name = request.form['name']
    price = request.form['price']
    print name, price
    product= Product(name,price)
    db.session.add(product)
    db.session.commit()

    products = Product.query.all()
    return render_template("index.html", products=products)


@app.route('/post_buy', methods=['POST'])
def post_buy():
    stripe_token = request.form['stripeToken']
    email = request.form['stripeEmail']
    product_id = request.form['product_id']
    product_price=request.form['product_price']
    #product = Product.query.get(product_id)
    product = None
    try:
        charge = stripe.Charge.create(
                #amount=int(product.price * 100),
                amount=int(float(product_price)),                
                currency='eur',
                card=stripe_token,
                description=email)
    except stripe.CardError, e:
        return render_template('error.html',err=e)

    print charge
    
    purchase = Purchase(uuid=str(uuid.uuid4()),
            email=email,
            product=product,
            product_id=product_id
            
            )
    db.session.add(purchase)
    db.session.commit()
    print 'Everything is OK, start sending mail!'


    return redirect('/allpurchases')
    

@app.route('/allpurchases')
def allpurchases():
    allpurchases = Purchase.query.all()
    return render_template('/allpurchases.html',products=allpurchases)


if __name__ == '__main__':
    sys.exit(app.run(debug=True))

