from flask import Blueprint, render_template, request, redirect, url_for, flash
from . import db
from flask_login import login_required, current_user
from .models import User, Account, Transaction

from datetime import datetime

bank = Blueprint('bank', __name__)

MINIMUM = 1000

TRANSTYPES = ["DEPOSIT", "WITHDRAW", "INITiAL_DEPOSIT"]

STATUSES = ["COMPLETED", "FAILED"]


def check_trans_type(name):
    if name == TRANSTYPES[0]:
        return "DEPOSIT"
    elif name == TRANSTYPES[1]:
        return "WITHDRAW"
    else:
        return None

def generate_account_number(id):
    # get the last account number
    account_id = Account.query.filter_by(id=id).first()

    if account_id:
        stringified = str(account_id.id).zfill(12)
        return stringified

@bank.route('/bank/create_account')
# @login_required
def index():
    # if not current_user.is_system_user:
    #     flash("you are not allowed to view this page")
    #     return redirect(url_for('main.index'))


    return render_template('create_account.html', user=current_user)





@bank.route('/bank/create_account', methods=['POST'] )
# @login_required
def bank_create_post():
    # user = current_user  # associated with the user
    # if not current_user.is_system_user:
    #     flash("you are not allowed to view this page")
    #     return redirect(url_for('main.index'))



    account_type = "real"

    account_balance = request.form.get("amount")
    email = request.form.get("email")


    # check if email account exist
    user = User.query.filter_by(email=email).first() # if this returns a user, then the email already exists in database

    if not user: 
        flash('Email address does not exists')
        return redirect(url_for('bank.index'))

    try:
        account_balance = int(account_balance)
        if account_balance < MINIMUM:
            flash(f'Minimum of {MINIMUM} is required')
            return redirect(url_for('bank.index'))
    except:
        return redirect(url_for('bank.index'))

    date_created = datetime.utcnow()

    
    if Account.query.filter_by().count() < 1:
        admin_account_number = str(0).zfill(12)
        # create account with associated systemuser
        admin_account = Account(
            user = 1,
            account_number = admin_account_number,
            account_type = "world",
            account_balance = 0,
            date_created = date_created,
            modified = datetime.utcnow()
        )
        db.session.add(admin_account)
        db.session.commit()
 


    account = Account(
        user = user.id,
        # account_number = account_number,
        account_type = account_type,
        account_balance = account_balance,
        date_created = date_created,
        modified = datetime.utcnow()
    )

    
    
    db.session.add(account)
    db.session.commit()

    # created ... so now generate account number using id
  




    account_number = generate_account_number(account.id)

    account.account_number = account_number




    if int(account_number) == 0:
        account.account_balance = 0
        db.session.add(account)
        db.session.commit()

    if account_number:
        account.account_number = account_number
        db.session.add(account)
        db.session.commit()
    
    else:
        flash(f'error creating account number')


    flash(f'Success Creating an account')
    # create transaction
    transaction = Transaction(
        date = datetime.utcnow(),
        account = account.id,
        description = f"Initial deposit: {account_balance}",
        trans_type = TRANSTYPES[2],
        amount = account_balance,
        status = STATUSES[0],
        balance =  account_balance
    )


    db.session.add(transaction)
    db.session.commit()

    return redirect(url_for('bank.account_details', id=account.id))

@bank.route('/profile')
@login_required
def profile():
    return render_template('profile.html', name=current_user.name)



@bank.route('/account/<int:id>')
@login_required
def account_details(id):
    # print(account_number)

    account = Account.query.get_or_404(id)

    return render_template('account_details.html', account=account)


@bank.route('/bank/my_accounts')
@login_required
def my_accounts():
    # print(account_number)
    accounts = Account.query.filter_by(user=current_user.id)

    return render_template('my_accounts.html', accounts=accounts)



@bank.route('/bank/account/<int:id>/withdraw')
@login_required
def withdraw(id):
    # print(account_number)
    account = Account.query.get_or_404(id)

    # amount = request.form.get('amount')

    # print(amount)
    transactions = Transaction.query.filter_by(account=account.id)

    return render_template('withdraw.html', account=account, transactions=transactions)


@bank.route('/bank/account/<int:id>/withdraw', methods=['POST'])
@login_required
def withdraw_post(id):
    # print(account_number)
    account = Account.query.get_or_404(id)

    amount = request.form.get('amount')

    # id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy 000000000000
    # date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    # account = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=False)
    # description = db.Column(db.String(1000))
    # trans_type = db.Column(db.String(100))
    # amount = db.Column(db.Integer)
    # status = db.Column(db.String(100))
    # balance = db.Column(db.Integer)
    try:
        amount = int(amount)
    except:
        return "invalid entry"


    # check for amount

    if amount <= account.account_balance:
        print("amount", amount, "account_balance:", account.account_balance)
    else:
        flash(f"not enough amount in your account to withdraw {amount}") 
        return  redirect(url_for('bank.withdraw', id=id))

    if amount < 1:
        flash(f"error cannot withdraw a negative number") 
        return  redirect(url_for('bank.withdraw', id=id))




    # create transaction
    transaction = Transaction(
        date = datetime.utcnow(),
        account = account.id,
        description = f"withdraw money amount: {amount}",
        trans_type = TRANSTYPES[1],
        amount = amount,
        status = STATUSES[0],
        balance = account.account_balance - amount
    )


    db.session.add(transaction)
    db.session.commit()

    # if transaction succesful subtract from this account too
    account.account_balance -= amount
    account.modified = datetime.utcnow()

    db.session.add(account)
    db.session.commit()

    
    transactions = Transaction.query.filter_by(account=account.id)


    flash(f'Success withdrawing amount {amount}')

    return render_template('withdraw.html', account=account, transactions=transactions)




@bank.route('/bank/account/<int:id>/deposit')
@login_required
def deposit(id):
    # print(account_number)
    account = Account.query.get_or_404(id)

    # amount = request.form.get('amount')

    # print(amount)
    transactions = Transaction.query.filter_by(account=account.id)

    return render_template('deposit.html', account=account, transactions=transactions)



@bank.route('/bank/account/<int:id>/deposit', methods=['POST'])
@login_required
def deposit_post(id):
    # print(account_number)
    account = Account.query.get_or_404(id)

    amount = request.form.get('amount')

    # id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy 000000000000
    # date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    # account = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=False)
    # description = db.Column(db.String(1000))
    # trans_type = db.Column(db.String(100))
    # amount = db.Column(db.Integer)
    # status = db.Column(db.String(100))
    # balance = db.Column(db.Integer)
    try:
        amount = int(amount)
    except:
        return "invalid entry"

    
    # check
    if amount < 1:
        flash(f"error cannot deposit a negative number") 
        return  redirect(url_for('bank.deposit', id=id))
    


    # if amount <= account.account_balance:
    #     print("amount", amount, "account_balance:", account.account_balance)
    # else:
    #     flash(f"not enough amount in your account to withdraw") 

    # create transaction
    transaction = Transaction(
        date = datetime.utcnow(),
        account = account.id,
        description = f"deposit money amount: {amount}",
        trans_type = TRANSTYPES[0],
        amount = amount,
        status = STATUSES[0],
        balance = account.account_balance + amount,
    )


    db.session.add(transaction)
    db.session.commit()

    # if transaction succesful subtract from this account too
    account.account_balance += amount
    account.modified = datetime.utcnow()

    db.session.add(account)
    db.session.commit()

    
    transactions = Transaction.query.filter_by(account=account.id)

    flash(f"successfull deposit of amount {amount}") 

    return render_template('deposit.html', account=account, transactions=transactions)



@bank.route('/bank/account/<int:id>/transfer')
@login_required
def transfer(id):
    # print(account_number)
    account = Account.query.get_or_404(id)

    # amount = request.form.get('amount')

    # print(amount)
    transactions = Transaction.query.filter_by(account=account.id)
    formatted_trans = []
    for transaction in transactions:
        account = Account.query.filter_by(id=transaction.account).first()
        to_account = Account.query.filter_by(id=transaction.to_account).first()
        data = {
            "date": transaction.date,
            "account": account,
            "description": transaction.description,
           "trans_type" : transaction.trans_type,
            "amount" : transaction.amount,
            "status" : transaction.status,
            "balance" : transaction.balance,
            "to_account" : transaction.to_account

        }
        # print(data)
        formatted_trans.append(data)

    

    return render_template('bank_transfer.html', account=account, transactions=formatted_trans)

@bank.route('/bank/account/<int:id>/transfer', methods=['POST'])
@login_required
def transfer_post(id):
    # print(account_number)
    account = Account.query.get_or_404(id)

    amount = request.form.get('amount')

    account_number = request.form.get('account_number')

    # check if account number exist
    to_account = Account.query.filter_by(account_number=account_number).first()
    if not to_account:
        return "invalid acccount number"


    # id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy 000000000000
    # date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    # account = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=False)
    # description = db.Column(db.String(1000))
    # trans_type = db.Column(db.String(100))
    # amount = db.Column(db.Integer)
    # status = db.Column(db.String(100))
    # balance = db.Column(db.Integer)
    try:
        amount = int(amount)
    except:
        return "invalid entry"

    # if amount <= account.account_balance:
    #     print("amount", amount, "account_balance:", account.account_balance)
    # else:
    #     flash(f"not enough amount in your account to withdraw") 

    # check for amount

    if amount <= account.account_balance:
        print("amount", amount, "account_balance:", account.account_balance)
    
    else:
        flash(f"not enough amount in your account to transfer {amount}") 
        return  redirect(url_for('bank.transfer', id=id))

    if amount < 1:
        flash(f"cannot transfer a negative number") 
        return  redirect(url_for('bank.transfer', id=id))

    # create transaction to withdraw from my account
    transaction = Transaction(
        date = datetime.utcnow(),
        account = account.id,
        description = f"transfer money from {account.account_number} to {to_account.account_number} amount: {amount}",
        trans_type = TRANSTYPES[1],
        amount = amount,
        status = STATUSES[0],
        balance = account.account_balance - amount,
        to_account = to_account.id
    )


    db.session.add(transaction)
    db.session.commit()

    # if transaction succesful subtract from this account too
    account.account_balance -= amount
    account.modified = datetime.utcnow()

    db.session.add(account)
    db.session.commit()

    # add transaction for deposit om to_accoubt
    transaction = Transaction(
        date = datetime.utcnow(),
        account = to_account.id,
        description = f"received money from {account.account_number} to {to_account.account_number} amount: {amount}",
        trans_type = TRANSTYPES[0],
        amount = amount,
        status = STATUSES[0],
        balance = to_account.account_balance + amount,
        to_account = to_account.id
    )

    db.session.add(transaction)
    db.session.commit()

    # if transaction succesful subtract from this account too
    to_account.account_balance += amount
    to_account.modified = datetime.utcnow()

    db.session.add(account)
    db.session.commit()


    
    transactions = Transaction.query.filter_by(account=account.id)

    formatted_trans = []
    for transaction in transactions:
        account = Account.query.filter_by(id=transaction.account).first()
        to_account = Account.query.filter_by(id=transaction.to_account).first()
        data = {
            "date": transaction.date,
            "account": account,
            "description": transaction.description,
           "trans_type" : transaction.trans_type,
            "amount" : transaction.amount,
            "status" : transaction.status,
            "balance" : transaction.balance,
            "to_account" : transaction.to_account

        }
        # print(data)
        formatted_trans.append(data)
    

    user_to_account = User.query.filter_by(id=to_account.user).first()
    flash(f"succesful transfer of {amount} to  {user_to_account.name}'s account number{to_account.account_number} ") 
    return render_template('bank_transfer.html', account=account, transactions=formatted_trans)


@bank.route('/bank/account/<int:id>/transactions')
@login_required
def transactions(id):
    # print(account_number)
    account = Account.query.get_or_404(id)

    # amount = request.form.get('amount')

    # print(amount)
    transactions = Transaction.query.filter_by(account=account.id).order_by(-Transaction.id)
    formatted_trans = []
    for transaction in transactions:
        account = Account.query.filter_by(id=transaction.account).first()
        to_account = Account.query.filter_by(id=transaction.to_account).first()
        data = {
            "id": transaction.id,
            "date": transaction.date,
            "account": account,
            "description": transaction.description,
           "trans_type" : transaction.trans_type,
            "amount" : transaction.amount,
            "status" : transaction.status,
            "balance" : transaction.balance,
            "to_account" : to_account

        }
        # print(data)
        formatted_trans.append(data)

    return render_template('transactions.html', account=account, transactions=formatted_trans)