from marshmallow import Schema, fields, validate, pre_load


class LedgerCreateSchema(Schema):
    serial_no = fields.String(validate=validate.Length(max=30), missing=None)
    duty_officer = fields.String(required=True, validate=validate.Length(min=1, max=50))
    personnel = fields.String(validate=validate.Length(max=2000), missing=None)
    incident_time = fields.String(required=True)
    info_source = fields.String(required=True, validate=validate.Length(min=1, max=100))
    jurisdiction = fields.String(required=True, validate=validate.Length(min=1, max=100))
    case_category = fields.String(required=True, validate=validate.Length(min=1, max=50))
    case_basic_info = fields.String(required=True, validate=validate.Length(min=1, max=5000))
    on_site_personnel = fields.String(validate=validate.Length(max=200), missing=None)
    on_site_handling = fields.String(validate=validate.Length(max=5000), missing=None)
    analysis_situation = fields.String(validate=validate.Length(max=5000), missing=None)
    closure_status = fields.String(validate=validate.Length(max=3000), missing=None)
    follow_up = fields.String(validate=validate.Length(max=3000), missing=None)
    handover = fields.String(validate=validate.Length(max=2000), missing=None)
    is_closed = fields.Integer(validate=validate.OneOf([0, 1]), missing=0)
    is_escalated = fields.Integer(validate=validate.OneOf([0, 1]), missing=0)

    @pre_load
    def strip_empty_strings(self, data, **kwargs):
        result = {}
        for key, value in data.items():
            if isinstance(value, str) and value.strip() == "":
                result[key] = None
            else:
                result[key] = value
        return result


class LedgerUpdateSchema(Schema):
    serial_no = fields.String(validate=validate.Length(max=30), missing=None)
    duty_officer = fields.String(validate=validate.Length(min=1, max=50), missing=None)
    personnel = fields.String(validate=validate.Length(max=2000), missing=None)
    incident_time = fields.String(missing=None)
    info_source = fields.String(validate=validate.Length(min=1, max=100), missing=None)
    jurisdiction = fields.String(validate=validate.Length(min=1, max=100), missing=None)
    case_category = fields.String(validate=validate.Length(min=1, max=50), missing=None)
    case_basic_info = fields.String(validate=validate.Length(min=1, max=5000), missing=None)
    on_site_personnel = fields.String(validate=validate.Length(max=200), missing=None)
    on_site_handling = fields.String(validate=validate.Length(max=5000), missing=None)
    analysis_situation = fields.String(validate=validate.Length(max=5000), missing=None)
    closure_status = fields.String(validate=validate.Length(max=3000), missing=None)
    follow_up = fields.String(validate=validate.Length(max=3000), missing=None)
    handover = fields.String(validate=validate.Length(max=2000), missing=None)
    is_closed = fields.Integer(validate=validate.OneOf([0, 1]), missing=None)
    is_escalated = fields.Integer(validate=validate.OneOf([0, 1]), missing=None)

    @pre_load
    def strip_empty_strings(self, data, **kwargs):
        result = {}
        for key, value in data.items():
            if isinstance(value, str) and value.strip() == "":
                result[key] = None
            else:
                result[key] = value
        return result


class LedgerListSchema(Schema):
    page = fields.Integer(missing=1, validate=validate.Range(min=1))
    per_page = fields.Integer(missing=20, validate=validate.Range(min=1, max=100))
    keyword = fields.String(missing=None)
    jurisdiction = fields.String(missing=None)
    case_category = fields.String(missing=None)
    is_closed = fields.Integer(missing=None)
    is_escalated = fields.Integer(missing=None)
    date_from = fields.String(missing=None)
    date_to = fields.String(missing=None)
    sort_by = fields.String(
        missing="incident_time",
        validate=validate.OneOf(["incident_time", "created_at", "serial_no"])
    )
    sort_order = fields.String(
        missing="desc",
        validate=validate.OneOf(["asc", "desc"])
    )
