from app import db


class PoliceStation(db.Model):
    __tablename__ = "派出所"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    派出所_刑侦 = db.Column(db.String(100), nullable=False)

    @classmethod
    def init_defaults(cls):
        defaults = [
            "刑侦一中队",
            "刑侦二中队",
            "刑侦三中队",
            "刑侦四中队",
        ]
        for name in defaults:
            if not cls.query.filter_by(派出所_刑侦=name).first():
                db.session.add(cls(派出所_刑侦=name))
        db.session.commit()
