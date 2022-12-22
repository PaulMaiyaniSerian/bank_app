# bank_app
this is a bank application

this is a  small bank assignment app for client


## setup
create virtual env and install all requirements

pip install -r requirements.txt

## migrations for the db

export FLASK_APP=manage.py

flask db init

flask db migrate -m "initial migration"

flask db upgrade

## running the app

flask run or python manage.py run

