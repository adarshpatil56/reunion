import time
import uuid
from pymongo import MongoClient
import datetime
from flask_restful import Resource
from flask import Flask, request, jsonify, make_response
import bcrypt
import secrets
from flask_jwt_extended import (create_access_token, create_refresh_token, jwt_required)
client = MongoClient()
db = client.test

JWT_REFRESH_TOKEN_TIMEDELTA = datetime.timedelta(hours=24)
# 60 minutes token expiration time
JWT_ACCESS_TOKEN_TIMEDELTA = datetime.timedelta(minutes=60)
from flask_restful import Api
retailer_app = Flask(__name__, template_folder='../templates')
retailer_app.config['JWT_BLACKLIST_ENABLED'] = True
retailer_app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']
retailer_app.config['SECRET_KEY'] = "ecre(tkejkCodearrAY@#$%098765{}<retailer>"
retailer_app.config['JSON_SORT_KEYS'] = False
api = Api(retailer_app)


def generate_security_token(token_type: str = 'urlsafe', length: int = None):
    if token_type == 'urlsafe':
        return secrets.token_urlsafe(length)
    elif token_type == 'hex':
        return secrets.token_hex(length)
    else:
        return secrets.token_bytes(length)


def update_session_token(email, session_token):
    try:
        db.user_info.update({'email': email}, {'$set': {'session_token': session_token}})
    except Exception as e:
        return None

# User Authentication API


class UserAuth(Resource):
    def post(self):
        email = request.json.get('email', '')
        password = request.json.get('password')
        user_info = db.users.find_one({'email': email, 'is_deleted': False}, {"_id": 0})
        user = user_info if user_info else None
        if user is not None:
            checkpw = False
            if user.get('login_source') == 'portal':
                password = password.encode()
                checkpw = bcrypt.checkpw(password, user.get('password'))
            if checkpw is True:
                session_token = generate_security_token(token_type='urlsafe')
                update_session_token(email=email, session_token=session_token)
                user_claims = {'role_id': 1, 'permissions_id': "sample_id_111"}
                access_token = create_access_token(identity=user.get('email'), user_claims=user_claims,
                                                   expires_delta=JWT_ACCESS_TOKEN_TIMEDELTA)
                refresh_token = create_refresh_token(identity=user.get('email'), user_claims=user_claims,
                                                     expires_delta=JWT_REFRESH_TOKEN_TIMEDELTA)
                user_data = {'user_id': user.get('first_name'), 'first_name': user.get('first_name'),
                             'last_name': user.get('last_name'), 'phone_number': user.get('phone_number'), 'access_token': access_token,
                             'refresh_token': refresh_token, 'email': email, 'language': user.get('language', 'English'),}
                db.users.update({'email': email}, {'$set': {'access_token': access_token, 'refresh_token': refresh_token}})
                return make_response(jsonify({'status': "Success", 'message': "Logged In!", 'data': user_data}), 200)
            else:
                return make_response(jsonify({'status': "Failure", 'message': "Invalid credential"}), 200)
        else:
            return make_response(jsonify({'status': "Success", 'message': "Invalid credential"}), 200)


# Get user info API


class GetUser(Resource):
    @jwt_required
    def post(self):
        user_id = request.json.get('user_id', '')
        user_info = db.users.find_one({'user_id': user_id, 'is_deleted': False}, {"_id": 0})
        user = user_info if user_info else None
        if user is not None:
            user_data = {'user_id': user.get('user_id'), 'first_name': user.get('first_name'),
                         'last_name': user.get('last_name'), 'phone_number': user.get('phone_number'),
                         'email': user.get('email'), 'language': user.get('language', 'English')}
            return make_response(jsonify({'status': "Success", 'message': "User Info", 'data': user_data}), 200)
        else:
            return make_response(jsonify({'status': "Failure", 'message': "Invalid User ID"}), 200)


# follow / unfollow user


class FollowUser(Resource):
    @jwt_required
    def post(self):
        email = request.json.get('email', '')
        user_id = request.json.get('user_id', '')
        follow = request.json.get('follow', False)
        user_info = db.users.find_one({'user_id': user_id, 'is_deleted': False}, {"_id": 0})
        user = user_info if user_info else None
        if user is not None:
            user_data = {'user_id': user_id, 'first_name': user.get('first_name'), "is_deleted": False,
                         'last_name': user.get('last_name'), 'phone_number': user.get('phone_number'),
                         'email': user.get('email'), 'language': user.get('language', 'English'), "follow": follow}
            db.users_follow.update({'email': email, 'user_id': user_id}, {'$set': {**user_data}}, upsert=True)
            return make_response(jsonify({'status': "Success", 'message': "Follow user successfully", 'data': user_data}), 200)
        else:
            return make_response(jsonify({'status': "Failure", 'message': "Invalid User ID"}), 200)


# Upload or delete post, Note: can be possible with DELETE API method also


class UploadDeletePost(Resource):
    @jwt_required
    def post(self):
        email = request.json.get('email', '')
        user_id = request.json.get('user_id', '')
        post_request = request.json.get('post_request', 'add')
        post_id = str(uuid.uuid4().hex)[:10] + str(round(time.time()))
        title = request.json.get('title', '')
        description = request.json.get('description', '')
        user_info = db.users.find_one({'user_id': user_id, 'email': email, 'is_deleted': False}, {"_id": 0})
        user = user_info if user_info else None
        user_data = {}
        current_date = datetime.datetime.utcnow()
        if user is not None:
            if post_request == "add":
                user_data = {'user_id': user_id, 'email': user.get('email'), 'post_id': post_id, "title": title,
                             "description": description, 'is_deleted': False, "created_at": current_date, "like_post": [], "likes": 0}
                db.users_post.insert({'email': email, 'user_id': user_id}, {'$set': {**user_data}}, upsert=True)
            elif post_request == "delete":
                user_data = {'user_id': user_id, 'email': user.get('email'), 'post_id': post_id, "title": title,
                             "description": description, 'is_deleted': True}
                db.users_post.insert({'email': email, 'user_id': user_id}, {'$set': {**user_data}}, upsert=True)
            return make_response(jsonify({'status': "Success", 'message': "Follow user successfully", 'data': user_data}), 200)
        else:
            return make_response(jsonify({'status': "Failure", 'message': "Invalid User ID"}), 200)


# Like or Unlike a post, comment on post


class LikeUnlikeCommentPost(Resource):
    @jwt_required
    def post(self):
        email = request.json.get('email', '')
        user_id = request.json.get('user_id', '')
        like_request = request.json.get('post_request', False)
        comment_request = request.json.get('comment_request', False)
        comment_desc = request.json.get('comment_desc', '')
        post_id = str(uuid.uuid4().hex)[:10] + str(round(time.time()))
        user_info = db.users.find_one({'user_id': user_id, 'email': email, 'is_deleted': False}, {"_id": 0})
        user = user_info if user_info else None
        if user is not None:
            # Requirement was to set like and comment different way, but store like, comment in same object will help
            # to get total post related info in one dictionary
            if comment_request:
                # update comment against user_id level
                db.users_post.update({'email': email, 'user_id': user_id}, {'$set': {"like_post.user_id": user_id,
                                                        "like_post.comment_description": comment_desc}}, upsert=True)
                return make_response(jsonify({'status': "Success", 'message': "Comment Added successfully"}), 200)
            elif like_request:
                old_status = db.users_post.find_one({'post_id': post_id}, {'_id': 0, 'like_post': 1}).get('like_post')
                like = True if like_request else False
                current_status = {'user_id': user_id, "like": like, "comment_description": None}
                status = {**old_status, **current_status}
                likes_count = len([d for d in status if d['like'] in [True]])
                # can count number of like using True status like count
                db.users_post.update({'email': email, 'user_id': user_id},
                                     {'$set': {"like_post": status, "likes": likes_count}}, upsert=True)
                return make_response(jsonify({'status': "Success", 'message': "Like post successfully"}), 200)
        else:
            return make_response(jsonify({'status': "Failure", 'message': "Invalid User ID"}), 200)


api.add_resource(UserAuth, '/user/auth')
api.add_resource(GetUser, '/user/info')
api.add_resource(FollowUser, '/user/follow')
api.add_resource(UploadDeletePost, '/user/upload-delete-post')
api.add_resource(LikeUnlikeCommentPost, '/user/like-unlike-comment-post')
