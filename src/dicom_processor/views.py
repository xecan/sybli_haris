# import os
# from flask import Blueprint, request, current_app, redirect, url_for, render_template, flash
# from werkzeug.utils import secure_filename
# from sybil import Serie, Sybil
# from flask_login import login_required

# dicom_processor_bp = Blueprint('dicom_processor', __name__)
# model = Sybil("sybil_base")

# @dicom_processor_bp.route('/upload', methods=['GET', 'POST'])
# @login_required
# def upload():
#     if request.method == 'POST':
#         if 'dicom_file' not in request.files:
#             flash('No file part')
#             return redirect(request.url)
#         file = request.files['dicom_file']
#         if file.filename == '':
#             flash('No selected file')
#             return redirect(request.url)
#         if file and allowed_file(file.filename):
#             filename = secure_filename(file.filename)
#             filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
#             file.save(filepath)
#             dicom_paths = [filepath]
#             serie = Serie(dicom_paths)
#             scores = model.predict([serie])
#             values_list = [value for sublist in scores.scores for value in sublist]
#             scores_percentage = [round(score * 100, 2) for score in values_list]
#             return render_template('dicom_processor/results.html', scores=scores_percentage)
#     return render_template('dicom_processor/upload.html')

# def allowed_file(filename):
#     return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'dcm'

# # Be sure to import and register this blueprint in your main app.py
import os
from flask import Blueprint, request, current_app, redirect, url_for, render_template, flash, Response
from werkzeug.utils import secure_filename
from sybil import Serie, Sybil
from flask_login import login_required
from flask import session
import csv
from io import StringIO

dicom_processor_bp = Blueprint('dicom_processor', __name__)
model = Sybil("sybil_base")

@dicom_processor_bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        if 'dicom_file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['dicom_file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            dicom_paths = [filepath]
            serie = Serie(dicom_paths)
            scores = model.predict([serie])
            values_list = [value for sublist in scores.scores for value in sublist]
            scores_percentage = [round(score * 100, 2) for score in values_list]
            session['scores'] = scores_percentage
            return render_template('dicom_processor/results.html', scores=scores_percentage)
    return render_template('dicom_processor/upload.html')

@dicom_processor_bp.route('/download_csv')
@login_required
def download_csv():
    # Retrieve the scores from session
    scores_percentage = session.get('scores', [])
    if not scores_percentage:
        flash("No scores to download.")
        return redirect(url_for('dicom_processor.upload'))

    si = StringIO()
    cw = csv.writer(si)
    cw.writerow(['Cancer Prediction Values (%)'])  # Header row
    for score in scores_percentage:
        cw.writerow([score])

    output = si.getvalue()
    si.close()

    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=scores.csv"}
    )



def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'dcm'


