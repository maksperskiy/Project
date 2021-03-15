from flask import Flask, render_template, request, make_response, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from authorization import *
from config import *

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shop.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), unique=True, default='Product №'+id)
    desc = db.Column(db.Text, default='There is no description')
    desc_opt = db.Column(db.String(250), default='There is no description')
    date = db.Column(db.DateTime, default=datetime.utcnow)
    visibility = db.Column(db.Boolean, default=True)
    price = db.Column(db.Integer, nullable=True)
    categories = db.Column(db.String(250), nullable=True)
    image = db.Column(db.String(250), nullable=True)
    author = db.Column(db.String(250), nullable=True)
    availability = db.Column(db.Integer, nullable=True)
    assignment = db.Column(db.String(250), nullable=True)
    material = db.Column(db.String(250), nullable=True)
    material_opt = db.Column(db.String(250), nullable=True)
    color = db.Column(db.String(250), nullable=True)
    color_opt = db.Column(db.String(250), nullable=True)
    size = db.Column(db.String(250), nullable=True)
    weight = db.Column(db.String(250), nullable=True)
    guarantee = db.Column(db.String(250), nullable=True)

    def __repr__(self):
        return 'Article %r' % self.id


@app.route('/')
def index():
    products = Product.query.order_by(Product.date).all()
    return render_template("index.html", products=products)


@app.route('/product/<int:id>')
def product(id):
    product = Product.query.get(id)
    return render_template("product.html", product=product)


@app.route('/admin')
@auth_required
def admin():
    products = Product.query.order_by(Product.date).all()
    return render_template("admin.html", products=products)


@app.route('/create', methods=['POST', 'GET'])
@auth_required
def create():
    if request.method == "POST":
        title = request.form['title']
        desc = request.form['desc']
        desc_opt = request.form['desc_opt']

        product = Product(title=title,
                          desc=desc,
                          desc_opt=desc_opt)

        try:
            db.session.add(product)
            db.session.commit()
            return redirect('/')
        except:
            return "ERROR"
    else:
        return render_template("create.html")


@app.route('/product/<int:id>/edit', methods=['POST', 'GET'])
@auth_required
def edit(id):
    product = Product.query.get(id)
    if request.method == "POST":
        product.title = request.form['title']
        product.desc = request.form['desc']
        product.desc_opt = request.form['desc_opt']
        try:
            db.session.commit()
            return redirect('/admin')
        except:
            return "ERROR"
    else:
        return render_template("edit.html", product=product)


@app.route('/product/<int:id>/del')
@auth_required
def delete(id):
    product = Product.query.get_or_404(id)
    try:
        db.session.delete(product)
        db.session.commit()
        return redirect('/admin')
    except:
        return "ERROR"


if __name__ == '__main__':
    app.run(debug=True, port=4567)




