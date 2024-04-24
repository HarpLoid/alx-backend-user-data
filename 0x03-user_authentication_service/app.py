#!/usr/bin/env python3
"""
Module - app
"""
from auth import Auth
from flask import Flask, Response
from flask import jsonify, abort, redirect, request


app = Flask(__name__)
AUTH = Auth()


@app.route("/", methods=["GET"])
def index() -> Response:
    """
    index route
    """
    return jsonify({"message": "Bienvenue"})


@app.route("/users", methods=["POST"])
def register() -> Response:
    """
    register route
    """
    email = request.form.get("email")
    pwd = request.form.get("password")

    try:
        AUTH.register_user(email, pwd)
        return jsonify({"email": email, "message": "user created"})
    except ValueError:
        return jsonify({"message": "email already registered"}), 400


@app.route("/sessions", methods=["POST"])
def login() -> Response:
    """
    login route
    """
    email = request.form.get("email")
    pwd = request.form.get("password")

    if AUTH.valid_login(email, pwd):
        session_id = AUTH.create_session(email)
        res = jsonify({"email": email, "message": "logged in"})
        res.set_cookie("session_id", session_id)
        return res

    abort(401)


@app.route("/sessions", methods=["DELETE"])
def logout() -> Response:
    """
    logout route
    """
    sess_id = request.cookies.get("session_id")

    user = AUTH.get_user_from_session_id(sess_id)
    if user:
        AUTH.destroy_session(user.id)
        return redirect("/")

    abort(403)


@app.route("/profile", methods=["GET"])
def profile() -> Response:
    """
    profile route
    """
    sess_id = request.cookies.get("session_id")

    user = AUTH.get_user_from_session_id(sess_id)
    if user is None:
        abort(403)

    return jsonify({"email": user.email}), 200


@app.route("/reset_password", methods=["POST"])
def get_reset_password_token() -> Response:
    """
    gets the reset password token
    """
    email = request.form.get("email")

    try:
        reset_tok = AUTH.get_reset_password_token(email)

        return jsonify({"email": email, "reset_token": reset_tok}), 200
    except ValueError:
        abort(403)


@app.route("/reset_password", methods=["PUT"])
def updated_password() -> Response:
    """
    updates the user's password
    """
    email = request.form.get("email")
    reset_token = request.form.get("reset_token")
    pwd = request.form.get("new_password")

    try:
        AUTH.update_password(reset_token, pwd)
        return jsonify({"email": email, "message": "Password updated"}), 200
    except ValueError:
        abort(403)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port="5000")
