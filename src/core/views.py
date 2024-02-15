from flask import Blueprint, render_template
from flask_login import login_required

core_bp = Blueprint("core", __name__)

@core_bp.route("/")
@login_required
def home():
    return render_template("core/index.html")

# Add a route for the predict window
@core_bp.route("/upload")
@login_required
def predict():
    # Assuming you have a template for the predict window named "predict.html"
    return render_template("core/predict.html")
