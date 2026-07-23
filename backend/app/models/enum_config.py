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
            ("command_center", "情指中心"),
            ("brigade_internal", "支队内部"),
            ("police_station", "派出所"),
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
            valid_codes = set()
            for i, (code, label) in enumerate(values):
                valid_codes.add(code)
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
                else:
                    existing.enum_label = label
                    existing.sort_order = i
                    existing.is_active = 1
            # Deactivate entries no longer in defaults
            stale = cls.query.filter(
                and_(cls.enum_type == enum_type, ~cls.enum_code.in_(valid_codes))
            ).all()
            for s in stale:
                s.is_active = 0
        db.session.commit()
