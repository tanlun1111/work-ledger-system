from datetime import datetime
from app import db
from app.models.base import BaseModel


class WorkLedger(BaseModel):
    __tablename__ = "work_ledger"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    serial_no = db.Column(db.String(30), nullable=False, unique=True, index=True)
    duty_officer = db.Column(db.String(50), nullable=False)
    personnel = db.Column(db.Text, nullable=True)
    incident_time = db.Column(db.DateTime, nullable=False, index=True)
    info_source = db.Column(db.String(100), nullable=False)
    jurisdiction = db.Column(db.String(100), nullable=False, index=True)
    case_category = db.Column(db.String(50), nullable=False, index=True)
    case_basic_info = db.Column(db.Text, nullable=False)
    on_site_personnel = db.Column(db.String(200), nullable=True)
    on_site_handling = db.Column(db.Text, nullable=True)
    analysis_situation = db.Column(db.Text, nullable=True)
    closure_status = db.Column(db.Text, nullable=True)
    follow_up = db.Column(db.Text, nullable=True)
    handover = db.Column(db.Text, nullable=True)
    is_closed = db.Column(db.Integer, nullable=False, default=0)
    is_escalated = db.Column(db.Integer, nullable=False, default=0)
    is_deleted = db.Column(db.Integer, nullable=False, default=0, index=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now, index=True)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    images = db.relationship("LedgerImage", backref="ledger", lazy="dynamic",
                             order_by="LedgerImage.sort_order, LedgerImage.id")

    __table_args__ = (
        db.Index("idx_closed_time", "is_closed", "incident_time"),
    )

    def to_list_item(self):
        from app.utils.helpers import truncate_text, format_datetime

        return {
            "id": self.id,
            "serial_no": self.serial_no,
            "duty_officer": self.duty_officer,
            "incident_time": format_datetime(self.incident_time),
            "jurisdiction": self.jurisdiction,
            "case_category": self.case_category,
            "info_source": self.info_source,
            "case_basic_info_summary": truncate_text(self.case_basic_info, 80),
            "is_closed": self.is_closed,
            "is_escalated": self.is_escalated,
            "image_count": self.images.count(),
            "created_at": format_datetime(self.created_at, "%Y-%m-%d %H:%M:%S"),
            "updated_at": format_datetime(self.updated_at, "%Y-%m-%d %H:%M:%S"),
        }

    def to_detail(self):
        from app.utils.helpers import format_datetime

        data = {
            "id": self.id,
            "serial_no": self.serial_no,
            "duty_officer": self.duty_officer,
            "personnel": self.personnel or "",
            "incident_time": format_datetime(self.incident_time),
            "info_source": self.info_source,
            "jurisdiction": self.jurisdiction,
            "case_category": self.case_category,
            "case_basic_info": self.case_basic_info,
            "on_site_personnel": self.on_site_personnel or "",
            "on_site_handling": self.on_site_handling or "",
            "analysis_situation": self.analysis_situation or "",
            "closure_status": self.closure_status or "",
            "follow_up": self.follow_up or "",
            "handover": self.handover or "",
            "is_closed": self.is_closed,
            "is_escalated": self.is_escalated,
            "is_deleted": self.is_deleted,
            "created_at": format_datetime(self.created_at, "%Y-%m-%d %H:%M:%S"),
            "updated_at": format_datetime(self.updated_at, "%Y-%m-%d %H:%M:%S"),
            "images": [
                {
                    "id": img.id,
                    "uuid_filename": img.uuid_filename,
                    "original_name": img.original_name,
                    "file_size": img.file_size,
                    "mime_type": img.mime_type,
                    "sort_order": img.sort_order,
                    "url": f"/api/ledger/{self.id}/images/{img.uuid_filename}",
                }
                for img in self.images.all()
            ],
        }
        return data
