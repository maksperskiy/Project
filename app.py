from flask import Flask, render_template, request, make_response, redirect, send_from_directory, url_for
from flask_paginate import Pagination, get_page_parameter
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.expression import func
import os
import random
from pathlib import Path
from werkzeug.utils import secure_filename
from datetime import datetime
from authorization import *
from config import *

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shop.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

db = SQLAlchemy(app)


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), default='Product №' + id)
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
        return 'Product %r' % self.id


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer)
    name = db.Column(db.String(25))
    phone = db.Column(db.String(15))
    address = db.Column(db.String(50))
    post_index = db.Column(db.String(10), nullable=True)
    email = db.Column(db.String(25))
    comment = db.Column(db.Text, nullable=True)
    processed = db.Column(db.Boolean, default=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    products = Product.query.filter(Product.visibility == True).filter(Product.categories != "").order_by(
        Product.date).all()

    four_popular_products = db.session.query(Product) \
        .outerjoin(Order, Product.id == Order.product_id) \
        .filter(Product.date >= datetime(datetime.today().year, datetime.today().month, day=1)) \
        .filter(Product.visibility == True) \
        .group_by(Product.id) \
        .order_by(db.func.count(Order.product_id).desc()) \
        .limit(4).all()

    four_products = Product.query.filter(Product.visibility == True).order_by(func.random()).limit(4).all()

    four_new_products = Product.query.filter(Product.visibility == True).order_by(Product.date.desc()).limit(4).all()

    categories = []
    cat_images = []
    for product in products:
        categories.append(product.categories)
        cat_images.append((product.image.split(' '))[0])

    cat_img = dict(zip(categories, cat_images))
    keys = list(set(cat_img.keys()))
    random.shuffle(keys)
    cat_img_shuffled = dict()
    for key in keys:
        cat_img_shuffled.update({key: cat_img[key]})

    categories = []
    cat_images = []
    for c, i in cat_img_shuffled.items():
        categories.append(c)
        cat_images.append(i)

    return render_template("index.html",
                           four_popular_products=four_popular_products,
                           four_products=four_products,
                           four_new_products=four_new_products,
                           categories=categories[:5],
                           cat_images=cat_images[:5])


@app.route('/search/', methods=['POST'])
def search():
    if request.method == "POST":
        products = Product.query.order_by(Product.date).all()
        search = request.form['search'].lower()
        sorted = []
        for p in products:
            if (search in p.title.lower() \
                or search in p.desc.lower() \
                or search in p.desc_opt.lower() \
                or search in p.author.lower() \
                or search in p.categories.lower() \
                or search in p.material.lower() \
                or search in p.material_opt.lower() \
                or search in p.color.lower() \
                or search in p.color_opt.lower()) \
                    and p.visibility:
                sorted.append(p)
        sorted = list(set(sorted))
        if not sorted:
            return render_template("not_found.html")
    return render_template("search.html", sorted=sorted, search=search)


@app.route('/product/<int:id>')
def product(id, success=0):
    product = Product.query.get(id)
    if not product or not product.visibility:
        return render_template("not_found.html")

    four_products = Product.query\
        .filter(Product.categories == product.categories)\
        .filter(Product.title != product.title)\
        .limit(4).all()

    return render_template("product.html", product=product, success=success, four_products=four_products)


@app.route('/all_products/<int:page_num>')
def all_products(page_num=1):
    products = Product.query.filter(Product.visibility == True).order_by(Product.date).paginate(per_page=12,
                                                                                                page=page_num,
                                                                                                error_out=True)

    return render_template('all_products.html', products=products)


@app.route('/categories/')
def categories():
    products = Product.query.filter(Product.visibility == True).filter(Product.categories != "").all()
    categories = []
    cat_images = []
    for product in products:
        categories.append(product.categories)
        cat_images.append(product.image)

    cat_img = dict(zip(categories, cat_images))

    categories = []
    cat_images = []
    for c, i in cat_img.items():
        categories.append(c)
        cat_images.append((i.split(' '))[0])

    return render_template("categories.html", categories=categories, cat_images=cat_images)


@app.route('/category/<category>')
def category_product(category):
    products = Product.query.all()
    sorted = []
    for product in products:
        if category == product.categories and product.visibility:
            sorted.append(product)
    if not sorted:
        return render_template("not_found.html")
    return render_template("category.html", sorted=sorted)


@app.route('/author/<author>')
def author_product(author):
    products = Product.query.all()
    sorted = []
    for product in products:
        if author == product.author and product.visibility:
            sorted.append(product)
    if not sorted:
        return render_template("not_found.html")
    return render_template("author.html", sorted=sorted)


@app.route('/admin')
@auth_required
def admin():
    products = Product.query.order_by(Product.date).all()
    orders = Order.query.order_by(Order.date).all()
    return render_template("admin.html", products=products, orders=orders)


@app.route('/create', methods=['POST', 'GET'])
@auth_required
def create():
    if request.method == "POST":
        title = request.form['title']
        desc = request.form['desc']
        desc_opt = request.form['desc_opt']
        images = request.files.getlist('image[]')
        visibility = True if request.form.get('visibility') else False
        price = request.form['price']
        categories = request.form['categories']
        author = request.form['author']
        availability = request.form['availability']
        assignment = request.form['assignment']
        material = request.form['material']
        material_opt = request.form['material_opt']
        color = request.form['color']
        color_opt = request.form['color_opt']
        size = request.form['size']
        weight = request.form['weight']
        guarantee = request.form['guarantee']

        files = ''

        for image in images:
            if image and allowed_file(image.filename):
                filename = secure_filename(image.filename)
                image.save(os.path.join(os.path.abspath(os.curdir), 'static\\images\\dest\\photo', filename))
                files += 'images/dest/photo/' + str(filename) + ' '
                print(filename)

        product = Product(title=title,
                          desc=desc,
                          desc_opt=desc_opt,
                          image=files,
                          visibility=visibility,
                          price=price,
                          categories=categories,
                          author=author,
                          availability=availability,
                          assignment=assignment,
                          material=material,
                          material_opt=material_opt,
                          color=color,
                          color_opt=color_opt,
                          size=size,
                          weight=weight,
                          guarantee=guarantee)

        try:
            db.session.add(product)
            db.session.commit()
            return redirect('/admin')
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
        product.visibility = True if request.form.get('visibility') else False
        product.price = request.form['price']
        product.categories = request.form['categories']
        product.author = request.form['author']
        product.availability = request.form['availability']
        product.assignment = request.form['assignment']
        product.material = request.form['material']
        product.material_opt = request.form['material_opt']
        product.color = request.form['color']
        product.color_opt = request.form['color_opt']
        product.size = request.form['size']
        product.weight = request.form['weight']
        product.guarantee = request.form['guarantee']

        images = request.files.getlist('image[]')
        files = ''

        for image in images:
            if image and allowed_file(image.filename):
                filename = secure_filename(image.filename)
                image.save(os.path.join(os.path.abspath(os.curdir), 'static\\images\\dest\\photo', filename))
                files += 'images/dest/photo/' + str(filename) + ' '
                print(filename)

        product.image = files

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


@app.route('/images/<filename>')
def uploaded_file(filename):
    return send_from_directory('/images/', filename)


@app.route('/buy/<int:product_id>', methods=['POST'])
def buy(product_id):
    name = request.form['name']
    phone = request.form['phone']
    address = request.form['address']
    post_index = request.form['post_index']
    email = request.form['email']
    comment = request.form['comment']

    if name and phone and address:
        if len(name) <= 30 and \
                len(address) <= 30 and \
                len(post_index) <= 6 and \
                len(email) <= 25:
            order = Order(product_id=product_id,
                          name=name,
                          phone=phone,
                          address=address,
                          email=email,
                          post_index=post_index,
                          comment=comment)

    try:
        db.session.add(order)
        db.session.commit()
        return product(product_id, success=1)
    except:
        return product(product_id, success=2)


@app.route('/order/<int:id>/process')
@auth_required
def order_process(id):
    order = Order.query.get(id)

    order.processed = not order.processed

    try:
        db.session.commit()
        return redirect('/admin')
    except:
        return "ERROR"


@app.route('/order/<int:id>/del')
@auth_required
def order_delete(id):
    order = Order.query.get_or_404(id)
    try:
        db.session.delete(order)
        db.session.commit()
        return redirect('/admin')
    except:
        return "ERROR"


@app.route('/product/<int:id>/visibility')
@auth_required
def product_visibility(id):
    product = Product.query.get(id)

    product.visibility = not product.visibility

    try:
        db.session.commit()
        return redirect('/admin')
    except:
        return "ERROR"


# db.session.query(Product.id, db.func.count(Order.product_id)).outerjoin(Order, Product.id == Order.product_id).filter(Product.date >= datetime(datetime.today().year, datetime.today().month, day=1)).group_by(Product.id).order_by(db.func.count(Order.product_id).desc()).limit(4).all()


if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=4567)
