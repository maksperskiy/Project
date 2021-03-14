from flask import Flask, render_template, request, make_response
from authorization import *
from config import *

app = Flask(__name__)


@app.route('/')
def index():
    return "<h1>ЭЭЭЭЭ хуй</h1>"


@app.route('/home')
@auth_required
def home():
    return "<h1>ничосе</h1>"


@app.route('/admin')
@auth_required
def admin():
    return "<h1>admin real shit nigga</h1>"


if __name__ == '__main__':
    app.run(debug=True)




