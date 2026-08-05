from flask import Blueprint, jsonify, request, current_app, send_file, g
from app import csrf
from app.utils.response import success
from app.utils.auth import login_required
from app.services import ledger_service, image_service, serial_service, enum_service, investigation_flow_service
from app.schemas.ledger_schema import LedgerCreateSchema, LedgerUpdateSchema, LedgerListSchema
from app.errors.exceptions import NotFoundException

api_bp = Blueprint("api", __name__)
csrf.exempt(api_bp)

ledger_create_schema = LedgerCreateSchema()
ledger_update_schema = LedgerUpdateSchema()
ledger_list_schema = LedgerListSchema()


@api_bp.route("/ledger", methods=["POST"])
@login_required
def create_ledger():
    data = request.get_json(silent=True) or {}
    validated = ledger_create_schema.load(data)
    ledger = ledger_service.create_ledger(validated)
    return success({"id": ledger.id, "serial_no": ledger.serial_no}, "台账登记成功")


@api_bp.route("/ledger/<int:ledger_id>", methods=["PATCH"])
@login_required
def update_ledger(ledger_id):
    data = request.get_json(silent=True) or {}
    validated = ledger_update_schema.load(data)
    filtered = {k: v for k, v in validated.items() if v is not None}
    ledger = ledger_service.update_ledger(ledger_id, filtered)
    return success({"id": ledger.id}, "台账更新成功")


@api_bp.route("/ledger/<int:ledger_id>", methods=["DELETE"])
@login_required
def delete_ledger(ledger_id):
    ledger_service.delete_ledger(ledger_id)
    return success(message="台账已删除")


@api_bp.route("/ledger/<int:ledger_id>", methods=["GET"])
@login_required
def get_ledger(ledger_id):
    ledger = ledger_service.get_ledger_detail(ledger_id)
    return success(ledger.to_detail())


@api_bp.route("/ledger", methods=["GET"])
@login_required
def list_ledgers():
    params = request.args.to_dict()
    for key in ["page", "per_page", "is_closed", "is_escalated"]:
        if key in params and params[key] != "" and params[key] is not None:
            try:
                params[key] = int(params[key])
            except (ValueError, TypeError):
                del params[key]
        elif key in params and params[key] == "":
            params[key] = None

    validated = ledger_list_schema.load(params)
    result = ledger_service.list_ledgers(validated)
    return success(result)


@api_bp.route("/ledger/next-serial", methods=["GET"])
@login_required
def next_serial():
    serial_no = serial_service.generate_serial_no()
    return success({"serial_no": serial_no})


@api_bp.route("/ledger/<int:ledger_id>/images", methods=["POST"])
@login_required
def upload_images(ledger_id):
    ledger = ledger_service.get_ledger_detail(ledger_id)
    files = request.files.getlist("files")
    if not files:
        return success({"images": []}, "没有文件上传")
    images = image_service.upload_attachments(ledger.id, files)
    return success({"images": images}, "上传成功")


@api_bp.route("/ledger/<int:ledger_id>/images/<uuid_filename>", methods=["GET"])
@login_required
def serve_image(ledger_id, uuid_filename):
    file_path, mime_type, original_name = image_service.get_attachment_path(ledger_id, uuid_filename)
    return send_file(file_path, mimetype=mime_type, as_attachment=False if mime_type.startswith("image/") else True, download_name=original_name)


@api_bp.route("/ledger/<int:ledger_id>/images/<int:image_id>", methods=["DELETE"])
@login_required
def delete_image(ledger_id, image_id):
    image_service.delete_attachment(ledger_id, image_id)
    return success(message="附件已删除")


@api_bp.route("/enums", methods=["GET"])
@login_required
def get_enums():
    result = enum_service.get_active_enums()
    return success(result)


@api_bp.route("/change-password", methods=["POST"])
@login_required
def change_password():
    data = request.get_json(silent=True) or {}
    old_pw = data.get("old_password", "")
    new_pw = data.get("new_password", "")

    if not old_pw or not new_pw:
        return jsonify({"code": 400, "message": "请填写旧密码和新密码", "data": {}}), 400

    if len(new_pw) < 6:
        return jsonify({"code": 400, "message": "新密码最少 6 位", "data": {}}), 400

    if not g.current_user.check_password(old_pw):
        return jsonify({"code": 400, "message": "旧密码错误", "data": {}}), 400

    g.current_user.set_password(new_pw)
    from app import db
    db.session.commit()

    return success(message="密码修改成功")


@api_bp.route("/me")
@login_required
def get_me():
    user = g.current_user
    return success({
        "id": user.id,
        "username": user.username,
        "display_name": user.display_name,
        "role": user.role,
    })


# ─── 侦察流 ────────────────────────────────────────────────────────

@api_bp.route("/ledger/<int:ledger_id>/investigation-flows", methods=["GET"])
@login_required
def list_investigation_flows(ledger_id):
    flows = investigation_flow_service.list_flows(ledger_id)
    return success(flows)


@api_bp.route("/ledger/<int:ledger_id>/investigation-flows", methods=["POST"])
@login_required
def create_investigation_flow(ledger_id):
    data = request.get_json(silent=True) or {}
    flow = investigation_flow_service.create_flow(ledger_id, data)
    return success({"id": flow.id}, "侦察流添加成功")


@api_bp.route("/investigation-flow/<int:flow_id>", methods=["GET"])
@login_required
def get_investigation_flow(flow_id):
    flow = investigation_flow_service.get_flow(flow_id)
    return success(flow.to_dict())


@api_bp.route("/investigation-flow/<int:flow_id>", methods=["PATCH"])
@login_required
def update_investigation_flow(flow_id):
    data = request.get_json(silent=True) or {}
    flow = investigation_flow_service.update_flow(flow_id, data)
    return success({"id": flow.id}, "侦察流更新成功")


@api_bp.route("/investigation-flow/<int:flow_id>", methods=["DELETE"])
@login_required
def delete_investigation_flow(flow_id):
    investigation_flow_service.delete_flow(flow_id)
    return success(message="侦察流已删除")


@api_bp.route("/investigation-flow/<int:flow_id>/attachments", methods=["POST"])
@login_required
def upload_flow_attachment(flow_id):
    files = request.files.getlist("files")
    if not files:
        return success({"attachments": []}, "没有文件上传")
    attachments = investigation_flow_service.upload_attachment(flow_id, files)
    return success({"attachments": attachments}, "上传成功")


@api_bp.route("/investigation-flow/<int:flow_id>/attachments/<uuid_filename>", methods=["GET"])
@login_required
def serve_flow_attachment(flow_id, uuid_filename):
    file_path, mime_type, original_name = investigation_flow_service.get_attachment_path(flow_id, uuid_filename)
    return send_file(file_path, mimetype=mime_type, as_attachment=False if mime_type.startswith("image/") else True, download_name=original_name)


@api_bp.route("/investigation-flow/<int:flow_id>/attachments/<int:attachment_id>", methods=["DELETE"])
@login_required
def delete_flow_attachment(flow_id, attachment_id):
    investigation_flow_service.delete_attachment(flow_id, attachment_id)
    return success(message="附件已删除")
