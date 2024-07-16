from flask import Flask
from flask_sqlalchemy import SQLAlchemy


app = Flask(_name_)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Extensions
db = SQLAlchemy(app)

if _name_ == '_main_':
    app.run(debug=True)