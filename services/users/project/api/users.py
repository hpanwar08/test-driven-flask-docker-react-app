from flask import Blueprint, request, render_template
from flask_restful import Resource, Api
from sqlalchemy import exc

from project.api.models import User
from project import db


users_blueprint = Blueprint('users', __name__, template_folder='./templates')
api = Api(users_blueprint)


@users_blueprint.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        db.session.add(User(username=username, email=email))
        db.session.commit()
    users = User.query.all()
    return render_template('index.html', users=users)


class UsersPing(Resource):
    def get(self):
        return {
            'status': 'success',
            'message': 'pong!'
            }


class UsersList(Resource):
    def post(self):
        response_body = {
            'status': 'fail',
            'message': 'Invalid json'
        }
        post_data = request.get_json()
        if not post_data:
            return response_body, 400
        username = post_data.get('username')
        email = post_data.get('email')
        try:
            user = User.query.filter_by(email=email).first()
            if not user:
                db.session.add(User(username=username, email=email))
                db.session.commit()
                response_body['status'] = 'Success'
                response_body['message'] = f'{email} was added'
                return response_body, 201
            else:
                response_body['message'] = f'Sorry. {email} already exists'
                return response_body, 400
        except exc.IntegrityError:
            db.session.rollback()
            return response_body, 400

    def get(self):
        users = User.query.all()
        response_body = {
            'status': 'success',
            'data': [user.to_json() for user in users]
        }
        return response_body, 200


class Users(Resource):
    def get(self, user_id):
        response_body = {
            'status': 'fail',
            'message': 'User does not exists'
        }
        try:
            user = User.query.filter_by(id=int(user_id)).first()
            if user:
                response_body = {
                    'status': 'success',
                    'data': {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email
                        }
                    }
                return response_body, 200
            else:
                return response_body, 404
        except ValueError:
            return response_body, 404


api.add_resource(UsersPing, '/users/ping')
api.add_resource(UsersList, '/users')
api.add_resource(Users, '/user/<user_id>')
