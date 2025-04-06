# rhyme.py
import os
from flask import Blueprint, render_template, request, redirect, url_for, send_from_directory, current_app
from werkzeug.utils import secure_filename

rhyme_bp = Blueprint('rhyme', __name__, template_folder='templates')

uploaded_notes = []

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@rhyme_bp.route('/notes')
def notes():
    return render_template('notes.html', notes=uploaded_notes)

@rhyme_bp.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files.get('file')
        subject = request.form.get('subject')
        topic = request.form.get('topic')
        yt_link = request.form.get('yt_link')

        filename = ""
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
            file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))

        note = {
            'id': len(uploaded_notes),
            'subject': subject,
            'topic': topic,
            'file': filename,
            'yt_link': yt_link
        }
        uploaded_notes.append(note)
        return redirect(url_for('rhyme.preview_notes'))

    return render_template('upload.html', note=None)

@rhyme_bp.route('/update/<int:note_id>', methods=['GET', 'POST'])
def update_note(note_id):
    note = next((n for n in uploaded_notes if n['id'] == note_id), None)
    if not note:
        return "Note not found", 404

    if request.method == 'POST':
        note['subject'] = request.form['subject']
        note['topic'] = request.form['topic']
        note['yt_link'] = request.form['yt_link']

        file = request.files.get('file')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
            note['file'] = filename

        return redirect(url_for('rhyme.preview_notes'))

    return render_template('upload.html', note=note)

@rhyme_bp.route('/uploads/<filename>')
def serve_note_file(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)

@rhyme_bp.route('/preview')
def preview_notes():
    return render_template('view_notes.html', notes=uploaded_notes)
