from datetime import datetime
from app import db
from app.models.ledger import WorkLedger


def generate_serial_no():
    today_prefix = f"JQ-{datetime.now():%Y%m%d}-"

    last = (
        WorkLedger.query
        .filter(WorkLedger.serial_no.like(f"{today_prefix}%"))
        .order_by(WorkLedger.serial_no.desc())
        .first()
    )

    if last:
        try:
            last_num = int(last.serial_no.split("-")[-1])
            next_num = last_num + 1
        except (ValueError, IndexError):
            next_num = 1
    else:
        next_num = 1

    return f"{today_prefix}{next_num:04d}"
