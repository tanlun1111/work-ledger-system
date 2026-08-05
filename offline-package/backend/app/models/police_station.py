from app import db


class PoliceStation(db.Model):
    __tablename__ = "派出所"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    派出所_刑侦 = db.Column(db.String(100), nullable=False)

    @classmethod
    def init_defaults(cls):
        defaults = [
            "岳阳派出所",
            "中山派出所",
            "永丰派出所",
            "方松派出所",
            "广富林派出所",
            "石湖荡派出所",
            "新桥派出所",
            "车墩派出所",
            "荣乐东路派出所",
            "九亭派出所",
            "九里亭派出所",
            "洞泾派出所",
            "泗泾派出所",
            "城中路派出所",
            "佘山派出所",
            "佘北派出所",
            "小昆山派出所",
            "叶榭派出所",
            "新浜派出所",
            "泖港派出所",
            "大学城派出所",
            "度假区派出所",
            "贵德路派出所",
            "刑侦支队",
        ]
        for name in defaults:
            if not cls.query.filter_by(派出所_刑侦=name).first():
                db.session.add(cls(派出所_刑侦=name))
        db.session.commit()
