from datetime import datetime
from app import db


class BaseModel(db.Model):
    __abstract__ = True

    def to_dict(self):
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            if isinstance(value, datetime):
                value = value.strftime("%Y-%m-%d %H:%M:%S")
            result[column.name] = value
        return result
