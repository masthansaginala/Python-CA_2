from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(50), nullable=False, default='customer')

    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)

class Hotel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    price = db.Column(db.Float, nullable=False)
    admin_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
    data = request.form
    user = User(username=data['username'], email=data['email'], role='customer')
    user.set_password(data['password'])
    db.session.add(user)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/login', methods=['POST'])
def login():
    data = request.form
    user = User.query.filter_by(username=data['username']).first()
    if user and user.check_password(data['password']):
        session['user_id'] = user.id
        session['role'] = user.role
        if user.role == 'admin':
            return redirect(url_for('admin_dashboard'))
        else:
            return redirect(url_for('customer_dashboard'))
    return jsonify({'message': 'Invalid credentials'}), 401

@app.route('/admin-dashboard')
def admin_dashboard():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('home'))
    return render_template('admin_dashboard.html')

@app.route('/add-hotel', methods=['GET', 'POST'])
def add_hotel():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('home'))

    if request.method == 'POST':
        data = request.form
        hotel = Hotel(name=data['name'], description=data['description'], price=data['price'], admin_id=session['user_id'])
        db.session.add(hotel)
        db.session.commit()
        return jsonify({'message': 'Hotel added successfully'})

    return render_template('add_hotel.html')

@app.route('/view-hotels')
def view_hotels():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('home'))
    return render_template('view_hotels.html')

@app.route('/hotels', methods=['GET'])
def get_hotels():
    if 'user_id' not in session:
        return jsonify({'message': 'Permission denied'}), 403

    if session.get('role') == 'admin':
        hotels = Hotel.query.filter_by(admin_id=session['user_id']).all()
    else:
        hotels = Hotel.query.all()
    return jsonify([{'id': hotel.id, 'name': hotel.name, 'description': hotel.description, 'price': hotel.price} for hotel in hotels])

@app.route('/edit-hotel/<int:hotel_id>', methods=['GET', 'PUT'])
def edit_hotel(hotel_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('home'))

    hotel = Hotel.query.get_or_404(hotel_id)

    if request.method == 'PUT':
        data = request.form
        hotel.name = data['name']
        hotel.description = data['description']
        hotel.price = data['price']
        db.session.commit()
        return jsonify({'message': 'Hotel updated successfully'})

    return render_template('edit_hotel.html', hotel=hotel)

@app.route('/delete-hotel/<int:hotel_id>', methods=['DELETE'])
def delete_hotel(hotel_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('home'))

    hotel = Hotel.query.get_or_404(hotel_id)

    db.session.delete(hotel)
    db.session.commit()
    return jsonify({'message': 'Hotel deleted successfully'})

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)