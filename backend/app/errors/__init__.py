from marshmallow import ValidationError
from .exceptions import NotFoundException, ConflictException, ValidationException
from flask import jsonify
import logging

logger = logging.getLogger(__name__)


def register_error_handlers(app):
    @app.errorhandler(ValidationError)
    def handle_validation_error(e):
        messages = e.messages
        if isinstance(messages, dict):
            flat = []
            for field, msgs in messages.items():
                if isinstance(msgs, list):
                    flat.extend(msgs)
                else:
                    flat.append(str(msgs))
            msg = "; ".join(flat)
        else:
            msg = str(messages)
        return jsonify({"code": 400, "message": msg, "data": {}}), 400

    @app.errorhandler(400)
    def handle_400(e):
        msg = e.description if hasattr(e, "description") and e.description else "请求参数错误"
        return jsonify({"code": 400, "message": msg, "data": {}}), 400

    @app.errorhandler(NotFoundException)
    def handle_not_found(e):
        return jsonify({"code": 404, "message": e.message, "data": {}}), 404

    @app.errorhandler(ConflictException)
    def handle_conflict(e):
        return jsonify({"code": 409, "message": e.message, "data": {}}), 409

    @app.errorhandler(ValidationException)
    def handle_validation_exception(e):
        return jsonify({"code": 400, "message": e.message, "data": {}}), 400

    @app.errorhandler(404)
    def handle_404(e):
        return jsonify({"code": 404, "message": "资源不存在", "data": {}}), 404

    @app.errorhandler(500)
    def handle_500(e):
        logger.exception("Internal server error")
        return jsonify({"code": 500, "message": "服务器内部错误", "data": {}}), 500

    @app.errorhandler(Exception)
    def handle_unexpected(e):
        logger.exception("Unexpected error")
        return jsonify({"code": 500, "message": "服务器内部错误", "data": {}}), 500
