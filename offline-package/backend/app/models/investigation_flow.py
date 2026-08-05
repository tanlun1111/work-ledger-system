from datetime import datetime
from app import db
from app.models.base import BaseModel


class InvestigationFlow(BaseModel):
    __tablename__ = "investigation_flow"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ledger_id = db.Column(db.Integer, db.ForeignKey("work_ledger.id"), nullable=False, index=True)
    flow_type = db.Column(db.String(50), nullable=False)
    sub_type = db.Column(db.String(50), nullable=True)
    content = db.Column(db.Text, nullable=False)
    feedback_result = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    ledger = db.relationship("WorkLedger", backref="investigation_flows")

    attachments = db.relationship(
        "InvestigationFlowAttachment", backref="flow", lazy="dynamic",
        order_by="InvestigationFlowAttachment.sort_order, InvestigationFlowAttachment.id"
    )

    def to_dict(self):
        from app.utils.helpers import format_datetime
        return {
            "id": self.id,
            "ledger_id": self.ledger_id,
            "flow_type": self.flow_type,
            "sub_type": self.sub_type or "",
            "content": self.content,
            "feedback_result": self.feedback_result or "",
            "created_at": format_datetime(self.created_at, "%Y-%m-%d %H:%M:%S"),
            "updated_at": format_datetime(self.updated_at, "%Y-%m-%d %H:%M:%S"),
            "attachments": [
                {
                    "id": att.id,
                    "uuid_filename": att.uuid_filename,
                    "original_name": att.original_name,
                    "file_size": att.file_size,
                    "mime_type": att.mime_type,
                    "url": f"/api/investigation-flow/{self.id}/attachments/{att.uuid_filename}",
                }
                for att in self.attachments.all()
            ],
        }
