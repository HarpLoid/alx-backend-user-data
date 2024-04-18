#!/usr/bin/env python3
""" Module of Session Authentication views
"""
from os import getenv
from models.user import User
from api.v1.views import app_views
from flask import abort, jsonify, request


@app_views.route('/auth_session/login', methods=['POST'], strict_slashes=False)
def auth_session () -> str:
    """
    Auth Session View
    """
    email = request.form.get('email')
    pwd = request.form.get('password')
    
    if not email:
        return jsonify({'error': 'email missing'}), 400
    
    if not pwd:
        return jsonify({'error': 'password missing'}), 400
    
    users = User.search({'email': email})
    if users:
        for user in users:
            if user.is_valid_password(pwd):
                from api.v1.app import auth
                
                session_id = auth.create_session(user.id)
                session_key = getenv('SESSION_NAME')
                res = jsonify(user.to_json())
                res.set_cookie(session_key, session_id)
                
                return res, 200
            else:
                return jsonify({'error': 'wrong password'}), 401
    
    return jsonify({'error': 'no user found for this email'}), 404

@app_views.route('/auth_session/logout', methods=['DELETE'],
                 strict_slashes=False)
def logout() -> str:
    """Logs out the user by deleting the session"""
    from api.v1.app import auth
    if not auth.destroy_session(request):
        return abort(404)
    return jsonify({}), 200
