import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask
from config import config_map
from app import db
from app.models.user import User
from werkzeug.security import generate_password_hash

app = Flask(__name__)
app.config.from_object(config_map["development"])

from app.__init__ import _ensure_mysql_database
_ensure_mysql_database(app.config["SQLALCHEMY_DATABASE_URI"])

db.init_app(app)


def usage():
    print("""
用户管理脚本

用法:
  python manage.py create-user <username> <password> <display_name> [admin|user]
  python manage.py reset-password <username> <new_password>
  python manage.py list-users
  python manage.py disable-user <username>
  python manage.py enable-user <username>
""")


def create_user():
    if len(sys.argv) < 5:
        print("用法: python manage.py create-user <username> <password> <display_name> [admin|user]")
        return
    username = sys.argv[2]
    password = sys.argv[3]
    display_name = sys.argv[4]
    role = sys.argv[5] if len(sys.argv) > 5 else "user"

    with app.app_context():
        if User.query.filter_by(username=username).first():
            print(f"用户 {username} 已存在")
            return
        user = User(
            username=username,
            password_hash=generate_password_hash(password),
            display_name=display_name,
            role=role,
        )
        db.session.add(user)
        db.session.commit()
        print(f"用户 {username}（{display_name}，角色 {role}）创建成功")


def reset_password():
    if len(sys.argv) < 4:
        print("用法: python manage.py reset-password <username> <new_password>")
        return
    username = sys.argv[2]
    new_password = sys.argv[3]

    with app.app_context():
        user = User.query.filter_by(username=username).first()
        if not user:
            print(f"用户 {username} 不存在")
            return
        user.set_password(new_password)
        db.session.commit()
        print(f"用户 {username} 密码已重置")


def list_users():
    with app.app_context():
        users = User.query.all()
        print(f"{'ID':<5} {'用户名':<20} {'显示名称':<15} {'角色':<8} {'状态':<6} {'最后登录'}")
        print("-" * 80)
        for u in users:
            status = "启用" if u.is_active else "禁用"
            last = u.last_login_at.strftime("%Y-%m-%d %H:%M") if u.last_login_at else "-"
            print(f"{u.id:<5} {u.username:<20} {u.display_name:<15} {u.role:<8} {status:<6} {last}")


def disable_user():
    if len(sys.argv) < 3:
        print("用法: python manage.py disable-user <username>")
        return
    _set_user_active(sys.argv[2], 0)


def enable_user():
    if len(sys.argv) < 3:
        print("用法: python manage.py enable-user <username>")
        return
    _set_user_active(sys.argv[2], 1)


def _set_user_active(username, active):
    with app.app_context():
        user = User.query.filter_by(username=username).first()
        if not user:
            print(f"用户 {username} 不存在")
            return
        user.is_active = active
        db.session.commit()
        status = "启用" if active else "禁用"
        print(f"用户 {username} 已{status}")


if __name__ == "__main__":
    cmds = {
        "create-user": create_user,
        "reset-password": reset_password,
        "list-users": list_users,
        "disable-user": disable_user,
        "enable-user": enable_user,
    }
    if len(sys.argv) < 2 or sys.argv[1] not in cmds:
        usage()
    else:
        cmds[sys.argv[1]]()
