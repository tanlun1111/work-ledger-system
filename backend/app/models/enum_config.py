from app import db
from app.models.base import BaseModel


class EnumConfig(BaseModel):
    __tablename__ = "enum_config"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    enum_type = db.Column(db.String(50), nullable=False, index=True)
    enum_code = db.Column(db.String(50), nullable=False)
    enum_label = db.Column(db.String(100), nullable=False)
    sort_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Integer, default=1)

    DEFAULTS = {
        "info_source": [
            ("110_report", "110接报"),
            ("citizen_report", "群众报案"),
            ("superior_assign", "上级交办"),
            ("dept_transfer", "其他部门移交"),
            ("proactive", "主动发现"),
            ("other", "其他"),
        ],
        "case_category": [
            ("criminal", "刑事"),
            ("public_security", "治安"),
            ("traffic", "交通"),
            ("assistance", "求助"),
            ("dispute", "纠纷"),
            ("other", "其他"),
        ],
    }

    @classmethod
    def init_defaults(cls):
        from app import db
        from sqlalchemy import and_

        for enum_type, values in cls.DEFAULTS.items():
            for i, (code, label) in enumerate(values):
                existing = cls.query.filter(
                    and_(cls.enum_type == enum_type, cls.enum_code == code)
                ).first()
                if not existing:
                    item = cls(
                        enum_type=enum_type,
                        enum_code=code,
                        enum_label=label,
                        sort_order=i,
                        is_active=1,
                    )
                    db.session.add(item)
        db.session.commit()
