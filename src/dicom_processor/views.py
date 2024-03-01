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
        user_name = request.form.get('user_name')
        files = request.files.getlist('dicom_files')  # Change to getlist to handle multiple files
        
        if not files or files[0].filename == '':
            flash('No selected file', "danger")
            return redirect(request.url)
        
        dicom_paths = []
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                dicom_paths.append(filepath)
        
        if dicom_paths:
            serie = Serie(dicom_paths)
            scores = model.predict([serie])
            values_list = [value for sublist in scores.scores for value in sublist]
            scores_percentage = [round(score * 100, 2) for score in values_list]
            session['scores'] = scores_percentage
            session['user_name'] = secure_filename(user_name)
            clear_upload_folder()
            return render_template('dicom_processor/results.html', user_name=user_name, scores=scores_percentage)
        else:
            flash('No valid files uploaded', "danger")
            return redirect(request.url)
    return render_template('dicom_processor/upload.html')


@dicom_processor_bp.route('/download_csv')
@login_required
def download_csv():
    # Retrieve the scores from session
    scores_percentage = session.get('scores', [])
    user_name = session.get('user_name', 'scores') 
    if not scores_percentage:
        flash("No scores to download.")
        return redirect(url_for('dicom_processor.upload'))

    si = StringIO()
    cw = csv.writer(si)
    cw.writerow(['Xecan Cancer Prediction Percentage (%)'])  # Header row
    for score in scores_percentage:
        cw.writerow([score])

    output = si.getvalue()
    si.close()

    filename = f"{user_name}_prediction.csv"
    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )



def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'dcm'


def clear_upload_folder(upload_folder_path="./uploads"):
    for filename in os.listdir(upload_folder_path):
        file_path = os.path.join(upload_folder_path, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                pass
        except Exception as e:
            print(f'Failed to delete {file_path}. Reason: {e}')

