from flask import jsonify


def success(data=None, message="操作成功"):
    return jsonify({"code": 200, "message": message, "data": data or {}})


def error(code=400, message="请求参数错误"):
    return jsonify({"code": code, "message": message, "data": {}}), code
