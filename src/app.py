from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, Api
import json
from sqlalchemy.types import Text
from flask_jwt_extended import create_access_token, JWTManager, get_jwt_identity, jwt_required


app = Flask(__name__)
app.config['SECRET_KEY'] = 'SUPER-SECRET-KEY'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

api = Api(app)
jwt = JWTManager(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone_number = db.Column(db.String(10), nullable=False)
    first_name = db.Column(db.String(10), nullable=False)
    last_name = db.Column(db.String(10), nullable=False)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    birthdate = db.Column(db.String(10), nullable=True)
    favorite_brands = db.Column(db.String, nullable=True) 
    selected_brands = db.Column(db.String, nullable=True)  
    address = db.Column(db.String, nullable=True)
    pincode = db.Column(db.String(6), nullable=True)
    state = db.Column(db.String(100), nullable=True)
    city = db.Column(db.String(100), nullable=True)
    country = db.Column(db.String(100), nullable=True)
    shopping_preferences = db.Column(Text, nullable=True)
    profile_color = db.Column(db.String(20), nullable=True)

    def set_shopping_preferences(self, preferences):
        self.shopping_preferences = json.dumps(preferences)

    def get_shopping_preferences(self):
        return json.loads(self.shopping_preferences) if self.shopping_preferences else {}


with app.app_context():
    db.create_all()

class UserRegistration(Resource):
    def post(self):
        try:
            data = request.get_json()
            email = data.get('email')
            phone_number = data.get('phone_number')
            first_name = data.get('first_name')
            last_name = data.get('last_name')
            username = data.get('username')
            password = data.get('password')

            if not username or not password:
                return {'message': 'Missing username or password'}, 400
            if User.query.filter_by(username=username).first():
                return {'message': 'Username already exists'}, 400

            new_user = User(username=username, password=password,email=email, phone_number=phone_number, first_name=first_name, last_name=last_name,)
            db.session.add(new_user)
            db.session.commit()
            return {'message': 'User created successfully'}, 201
        except Exception as e:
            return {'message': str(e)}, 500

class UserLogin(Resource):
    def post(self):
        try:
            data = request.get_json()
            username = data.get('username')
            password = data.get('password')

            user = User.query.filter_by(username=username).first()

            if user and user.password == password:
                access_token = create_access_token(identity=user.id)
                return {'access_token': access_token}, 200

            return {'message': 'Invalid username or password'}, 401
        except Exception as e:
            return {'message': str(e)}, 500
        


class UserOnboarding(Resource):
    @jwt_required()
    def post(self):
        try:
            data = request.get_json()
            current_user_id = get_jwt_identity()
            user = User.query.get(current_user_id)

            if not user:
                return {'message': 'User not found'}, 404

            user.birthdate = data.get('birthdate', user.birthdate)
            user.favorite_brands = ','.join(data.get('favorite_brands', []))
            user.selected_brands = ','.join(data.get('selected_brands', []))
            user.address = data.get('address', user.address)
            user.pincode = data.get('pincode', user.pincode)
            user.state = data.get('state', user.state)
            user.city = data.get('city', user.city)
            user.country = data.get('country', user.country)
            user.set_shopping_preferences(data.get('shopping_preferences', user.get_shopping_preferences()))
            user.profile_color = data.get('profile_color', user.profile_color)

            db.session.commit()
            return {'message': 'Profile Updated Successfully!'}, 200
        except Exception as e:
            return {'message': str(e)}, 500



api.add_resource(UserOnboarding, '/api/v1/onboarding')
api.add_resource(UserRegistration, '/api/v1/register')
api.add_resource(UserLogin, '/api/v1/login')


if __name__ == '__main__':
    app.run(debug=True)
