from flask import Blueprint, render_template
from app.utils.auth import login_required

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
@login_required
def index():
    return render_template("index.html")


@main_bp.route("/ledger/add")
@login_required
def ledger_add():
    return render_template("ledger_form.html", mode="add")


@main_bp.route("/ledger/<int:ledger_id>/edit")
@login_required
def ledger_edit(ledger_id):
    return render_template("ledger_form.html", mode="edit", record_id=ledger_id)


@main_bp.route("/ledger/<int:ledger_id>/view")
@login_required
def ledger_view(ledger_id):
    return render_template("ledger_detail.html", record_id=ledger_id)
