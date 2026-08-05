from flask import Blueprint, render_template, request, redirect, url_for, session
from datetime import datetime
from app.models.user import User

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        if session.get("user_id"):
            return redirect(url_for("main.index"))
        error = request.args.get("error", "")
        expired = request.args.get("expired", "")
        return render_template("login.html", error=error, expired=expired)

    username = request.form.get("login_username", "").strip()
    password = request.form.get("password", "").strip()

    if not username or not password:
        return redirect(url_for("auth.login", error="请输入用户名和密码"))

    user = User.query.filter_by(username=username).first()
    if not user or not user.is_active or not user.check_password(password):
        return redirect(url_for("auth.login", error="用户名或密码错误"))

    session["user_id"] = user.id
    session.permanent = True
    user.last_login_at = datetime.now()
    from app import db
    db.session.commit()

    return redirect(url_for("main.index"))


@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))
