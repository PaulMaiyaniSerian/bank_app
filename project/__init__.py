from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
# init SQLAlchemy so we can use it later in our models

from sqlalchemy import create_engine


db = SQLAlchemy()
migrate = Migrate()


def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = 'secret-key-goes-here'
    # app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'


    # replace here with the mysql connection string
    # app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://tn243:0j1YqHL4CRkI@db.ethereallab.app:3306/tn243' # eg 'mysql:....'

    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:rKskryi2PwcsvCsFmGEV@containers-us-west-42.railway.app:5789/railway' # eg 'mysql:....'


    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        # since the user_id is just the primary key of our user table, use it in the query for the user
        return User.query.get(int(user_id))

    # migrate = Migrate(app, db)

    migrate.init_app(app, db)




    # blueprint for auth routes in our app
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    # blueprint for non-auth parts of app
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    # blueprint for bank 
    from .bank import bank as bank_blueprint
    app.register_blueprint(bank_blueprint)

    return app