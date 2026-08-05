from datetime import datetime

from app import db
from app.models.ledger import WorkLedger
from app.errors.exceptions import NotFoundException, ConflictException
from app.services.serial_service import generate_serial_no
from app.utils.helpers import parse_datetime


def create_ledger(data):
    serial_no = data.get("serial_no")
    if not serial_no:
        serial_no = generate_serial_no()

    existing = WorkLedger.query.filter_by(serial_no=serial_no).first()
    if existing:
        raise ConflictException(f"序号 {serial_no} 已存在")

    incident_time = parse_datetime(data["incident_time"])
    if not incident_time:
        raise ConflictException("发生时间格式错误，应为 YYYY-MM-DD HH:MM")

    ledger = WorkLedger(
        serial_no=serial_no,
        duty_officer=data["duty_officer"],
        personnel=data.get("personnel"),
        incident_time=incident_time,
        info_source=data["info_source"],
        jurisdiction=data["jurisdiction"],
        case_category=data["case_category"],
        case_basic_info=data["case_basic_info"],
        on_site_personnel=data.get("on_site_personnel"),
        on_site_handling=data.get("on_site_handling"),
        analysis_situation=data.get("analysis_situation"),
        closure_status=data.get("closure_status"),
        follow_up=data.get("follow_up"),
        handover=data.get("handover"),
        is_closed=data.get("is_closed", 0),
        is_escalated=data.get("is_escalated", 0),
    )

    db.session.add(ledger)
    db.session.commit()

    return ledger


def update_ledger(ledger_id, data):
    ledger = WorkLedger.query.filter_by(id=ledger_id, is_deleted=0).first()
    if not ledger:
        raise NotFoundException("台账记录不存在")

    if "serial_no" in data and data["serial_no"] is not None:
        existing = WorkLedger.query.filter(
            WorkLedger.serial_no == data["serial_no"],
            WorkLedger.id != ledger_id
        ).first()
        if existing:
            raise ConflictException(f"序号 {data['serial_no']} 已存在")
        ledger.serial_no = data["serial_no"]

    if "duty_officer" in data and data["duty_officer"] is not None:
        ledger.duty_officer = data["duty_officer"]

    if "personnel" in data and data["personnel"] is not None:
        ledger.personnel = data["personnel"] if data["personnel"] else None

    if "incident_time" in data and data["incident_time"] is not None:
        incident_time = parse_datetime(data["incident_time"])
        if not incident_time:
            raise ConflictException("发生时间格式错误")
        ledger.incident_time = incident_time

    for field in [
        "info_source", "jurisdiction", "case_category", "case_basic_info",
        "on_site_personnel", "on_site_handling", "analysis_situation",
        "closure_status", "follow_up", "handover",
    ]:
        if field in data and data[field] is not None:
            setattr(ledger, field, data[field])

    if "is_closed" in data and data["is_closed"] is not None:
        ledger.is_closed = data["is_closed"]

    if "is_escalated" in data and data["is_escalated"] is not None:
        ledger.is_escalated = data["is_escalated"]

    ledger.updated_at = datetime.now()
    db.session.commit()

    return ledger


def delete_ledger(ledger_id):
    ledger = WorkLedger.query.filter_by(id=ledger_id, is_deleted=0).first()
    if not ledger:
        raise NotFoundException("台账记录不存在")

    ledger.is_deleted = 1
    ledger.updated_at = datetime.now()
    db.session.commit()


def get_ledger_detail(ledger_id):
    ledger = WorkLedger.query.filter_by(id=ledger_id, is_deleted=0).first()
    if not ledger:
        raise NotFoundException("台账记录不存在")
    return ledger


def list_ledgers(params):
    query = WorkLedger.query.filter(WorkLedger.is_deleted == 0)

    keyword = params.get("keyword")
    if keyword:
        pattern = f"%{keyword}%"
        query = query.filter(
            db.or_(
                WorkLedger.serial_no.like(pattern),
                WorkLedger.personnel.like(pattern),
                WorkLedger.case_basic_info.like(pattern),
            )
        )

    if params.get("jurisdiction"):
        query = query.filter(WorkLedger.jurisdiction == params["jurisdiction"])

    if params.get("case_category"):
        query = query.filter(WorkLedger.case_category == params["case_category"])

    if params.get("is_closed") is not None:
        query = query.filter(WorkLedger.is_closed == params["is_closed"])

    if params.get("is_escalated") is not None:
        query = query.filter(WorkLedger.is_escalated == params["is_escalated"])

    if params.get("date_from"):
        try:
            dt = datetime.strptime(params["date_from"], "%Y-%m-%d")
            query = query.filter(WorkLedger.incident_time >= dt)
        except ValueError:
            pass

    if params.get("date_to"):
        try:
            dt = datetime.strptime(params["date_to"], "%Y-%m-%d")
            dt = dt.replace(hour=23, minute=59, second=59)
            query = query.filter(WorkLedger.incident_time <= dt)
        except ValueError:
            pass

    sort_by = params.get("sort_by", "incident_time")
    sort_order = params.get("sort_order", "desc")

    allowed_sorts = {
        "incident_time": WorkLedger.incident_time,
        "created_at": WorkLedger.created_at,
        "serial_no": WorkLedger.serial_no,
    }
    sort_col = allowed_sorts.get(sort_by, WorkLedger.incident_time)
    if sort_order == "asc":
        query = query.order_by(sort_col.asc())
    else:
        query = query.order_by(sort_col.desc())

    page = params.get("page", 1)
    per_page = params.get("per_page", 20)
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return {
        "items": [item.to_list_item() for item in pagination.items],
        "total": pagination.total,
        "page": pagination.page,
        "per_page": pagination.per_page,
        "total_pages": pagination.pages,
    }
