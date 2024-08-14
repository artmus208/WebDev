from flask import Blueprint
from flask import render_template

stub_bp = Blueprint("stub", __name__)

@stub_bp.route("/stub", methods=["GET"])
def get_stub():
    return render_template('stub.html') 