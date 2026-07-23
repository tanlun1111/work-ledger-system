from datetime import datetime
from app import db
from app.models.base import BaseModel


class InvestigationFlowAttachment(BaseModel):
    __tablename__ = "investigation_flow_attachments"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    flow_id = db.Column(db.Integer, db.ForeignKey("investigation_flow.id"), nullable=False, index=True)
    uuid_filename = db.Column(db.String(255), nullable=False)
    original_name = db.Column(db.String(255), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)
    mime_type = db.Column(db.String(50), nullable=False)
    sort_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.now)
