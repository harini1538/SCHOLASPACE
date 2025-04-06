from flask import Blueprint, render_template, request, redirect, send_from_directory, current_app
import os, json
from werkzeug.utils import secure_filename

stu_bp = Blueprint('stu', __name__, template_folder='templates')

TASK_FILE = 'tasks.json'

def load_tasks():
    try:
        with open(TASK_FILE, 'r') as f:
            return json.load(f)
    except:
        return []

def save_tasks(tasks):
    with open(TASK_FILE, 'w') as f:
        json.dump(tasks, f, indent=4)

@stu_bp.route('/stupo', methods=['GET', 'POST'])
def student_portal():
    tasks = load_tasks()
    if request.method == 'POST':
        title = request.form['task_title']
        file = request.files['file']
        if file and file.filename.endswith('.pdf'):
            filename = secure_filename(file.filename)
            path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(path)
            for task in tasks:
                if task['title'] == title:
                    task['status'] = 'Completed'
                    task['submission'] = filename
            save_tasks(tasks)
        return redirect('/stu/stupo')
    return render_template('stu.html', tasks=tasks)

@stu_bp.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)
