import os

from flask import Flask
from flask_jwt_extended import JWTManager

from controllers.book_controller import books_bp
from controllers.member_controller import members_bp
from controllers.user_controller import auth_bp

# Flask constructor takes the name of 
# current module (__name__) as argument.
app = Flask(__name__)
SECRET_KEY = os.environ.get('SECRET_KEY', 'my_precious')

app.config['SECRET_KEY'] = SECRET_KEY
jwt = JWTManager(app)
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(books_bp, url_prefix='/api')
app.register_blueprint(members_bp, url_prefix='/api')


# The route() function of the Flask class is a decorator,
# which tells the application which URL should call 
# the associated function.
@app.route('/')
def hello_world():
    return 'Hello World'


# main driver function
if __name__ == '__main__':
    # run() method of Flask class runs the application
    # on the local development server.
    app.run()
