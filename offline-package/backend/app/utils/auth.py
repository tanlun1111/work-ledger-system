from functools import wraps
from flask import session, redirect, url_for, request, jsonify, g
from app.models.user import User


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        user_id = session.get("user_id")
        if not user_id:
            if request.path.startswith("/api/"):
                return jsonify({"code": 401, "message": "请先登录", "data": {}}), 401
            return redirect(url_for("auth.login"))
        user = User.query.get(user_id)
        if not user or not user.is_active:
            session.clear()
            if request.path.startswith("/api/"):
                return jsonify({"code": 401, "message": "账号已被禁用", "data": {}}), 401
            return redirect(url_for("auth.login"))
        g.current_user = user
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        user_id = session.get("user_id")
        if not user_id:
            if request.path.startswith("/api/"):
                return jsonify({"code": 401, "message": "请先登录", "data": {}}), 401
            return redirect(url_for("auth.login"))
        user = User.query.get(user_id)
        if not user or not user.is_active:
            session.clear()
            if request.path.startswith("/api/"):
                return jsonify({"code": 401, "message": "账号已被禁用", "data": {}}), 401
            return redirect(url_for("auth.login"))
        if not user.is_admin():
            if request.path.startswith("/api/"):
                return jsonify({"code": 403, "message": "需要管理员权限", "data": {}}), 403
            return redirect(url_for("main.index"))
        return f(*args, **kwargs)
    return decorated
