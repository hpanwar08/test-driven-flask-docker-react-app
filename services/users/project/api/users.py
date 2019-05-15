from flask import Blueprint, request
from flask_restful import Resource, Api
from sqlalchemy import exc

from project.api.models import User
from project import db


users_blueprint = Blueprint('users', __name__)
api = Api(users_blueprint)


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


class Users(Resource):
    def get(self, user_id):
        user = User.query.filter_by(id=user_id).first()
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


api.add_resource(UsersPing, '/users/ping')
api.add_resource(UsersList, '/users')
api.add_resource(Users, '/user/<user_id>')
