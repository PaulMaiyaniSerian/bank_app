from . import db
from sqlalchemy.types import Boolean
from flask_login import UserMixin


from datetime import datetime

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(200))
    is_system_user = db.Column(Boolean, default=False)
    # accounts = db.relationship('Account', backref='user', lazy=True)



class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy 000000000000
    user = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)   # associated with the user
    account_number = db.Column(db.String(20), unique=True, nullable=True)
    account_type = db.Column(db.String(20), nullable=False, default="real")
    account_balance = db.Column(db.Integer, default=0)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    modified = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)

    # transactions = db.relationship('Transaction', backref='account')




class Transaction(db.Model):

    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy 000000000000
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


    account = db.Column(db.Integer, db.ForeignKey('account.id',ondelete='CASCADE' ), nullable=False)
    to_account = db.Column(db.Integer, db.ForeignKey('account.id', ondelete='CASCADE'), nullable=True)


    # acc = db.relationship('Account', foreign_keys=[account,])
    # to_acc = db.relationship('Account', foreign_keys=[to_account,])


    description = db.Column(db.String(200))
    trans_type = db.Column(db.String(100))
    amount = db.Column(db.Integer)
    status = db.Column(db.String(100), nullable=True)
    balance = db.Column(db.Integer, nullable=True)





