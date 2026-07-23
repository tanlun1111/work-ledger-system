import os
from datetime import datetime
from flask import current_app
from app import db
from app.models.investigation_flow import InvestigationFlow
from app.models.investigation_flow_attachment import InvestigationFlowAttachment
from app.models.ledger import WorkLedger
from app.errors.exceptions import NotFoundException
from app.utils import upload as upload_utils


def list_flows(ledger_id):
    flows = InvestigationFlow.query.filter_by(ledger_id=ledger_id).order_by(
        InvestigationFlow.created_at.desc()
    ).all()
    return [f.to_dict() for f in flows]


def get_flow(flow_id):
    flow = InvestigationFlow.query.get(flow_id)
    if not flow:
        raise NotFoundException("侦察流记录不存在")
    return flow


def create_flow(ledger_id, data):
    ledger = WorkLedger.query.filter_by(id=ledger_id, is_deleted=0).first()
    if not ledger:
        raise NotFoundException("台账记录不存在")

    flow = InvestigationFlow(
        ledger_id=ledger_id,
        flow_type=data.get("flow_type", ""),
        sub_type=data.get("sub_type", ""),
        content=data.get("content", ""),
        feedback_result=data.get("feedback_result", ""),
    )
    db.session.add(flow)
    db.session.commit()
    return flow


def update_flow(flow_id, data):
    flow = InvestigationFlow.query.get(flow_id)
    if not flow:
        raise NotFoundException("侦察流记录不存在")

    for field in ["flow_type", "sub_type", "content", "feedback_result"]:
        if field in data and data[field] is not None:
            setattr(flow, field, data[field])

    flow.updated_at = datetime.now()
    db.session.commit()
    return flow


def delete_flow(flow_id):
    flow = InvestigationFlow.query.get(flow_id)
    if not flow:
        raise NotFoundException("侦察流记录不存在")

    # Delete attachments files
    for att in flow.attachments.all():
        upload_utils.delete_file(att.uuid_filename)

    db.session.delete(flow)
    db.session.commit()


def upload_attachment(flow_id, files):
    flow = InvestigationFlow.query.get(flow_id)
    if not flow:
        raise NotFoundException("侦察流记录不存在")

    uploaded = []
    for file in files:
        if not file or not file.filename:
            continue

        safe_name, tmp_path = upload_utils.save_to_tmp(file)
        size = os.path.getsize(tmp_path)
        mime_type = file.content_type or "application/octet-stream"

        try:
            att = InvestigationFlowAttachment(
                flow_id=flow_id,
                uuid_filename=safe_name,
                original_name=file.filename,
                file_size=size,
                mime_type=mime_type,
            )
            db.session.add(att)
            db.session.flush()
            upload_utils.move_from_tmp(safe_name)
            uploaded.append({
                "id": att.id,
                "uuid_filename": att.uuid_filename,
                "original_name": att.original_name,
                "file_size": att.file_size,
                "mime_type": att.mime_type,
            })
        except Exception:
            upload_utils.cleanup_tmp(safe_name)
            db.session.rollback()
            raise

    db.session.commit()
    return uploaded


def delete_attachment(flow_id, attachment_id):
    att = InvestigationFlowAttachment.query.filter_by(
        id=attachment_id, flow_id=flow_id
    ).first()
    if not att:
        raise NotFoundException("附件不存在")

    safe_name = att.uuid_filename
    db.session.delete(att)
    db.session.commit()
    upload_utils.delete_file(safe_name)


def get_attachment_path(flow_id, uuid_filename):
    att = InvestigationFlowAttachment.query.filter_by(
        flow_id=flow_id, uuid_filename=uuid_filename
    ).first()
    if not att:
        raise NotFoundException("附件不存在")

    file_path = os.path.join(current_app.config["UPLOAD_FOLDER"], uuid_filename)
    if not os.path.exists(file_path):
        tmp_path = os.path.join(current_app.config["UPLOAD_TMP_FOLDER"], uuid_filename)
        if os.path.exists(tmp_path):
            file_path = tmp_path
        else:
            raise NotFoundException("附件文件不存在")

    return file_path, att.mime_type, att.original_name
