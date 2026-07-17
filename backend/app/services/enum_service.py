from app import db
from app.models.enum_config import EnumConfig
from app.models.ledger import WorkLedger
from app.models.police_station import PoliceStation


def get_active_enums():
    items = EnumConfig.query.filter(EnumConfig.is_active == 1).order_by(EnumConfig.sort_order).all()
    result = {}

    for item in items:
        if item.enum_type not in result:
            result[item.enum_type] = []
        result[item.enum_type].append({
            "value": item.enum_label,
            "label": item.enum_label,
        })

    stations = (
        PoliceStation.query
        .with_entities(PoliceStation.派出所_刑侦)
        .distinct()
        .order_by(PoliceStation.派出所_刑侦)
        .all()
    )
    result["jurisdiction"] = [
        {"value": s[0], "label": s[0]} for s in stations if s[0]
    ]

    return result
