# teacher_routes.py

from flask import Blueprint, render_template, request, redirect, url_for
from datetime import datetime
import json

# Blueprint name and template folder
teacher_bp = Blueprint('teacher', __name__, template_folder='templates')

TASK_FILE = 'tasks.json'

# Helper functions
def load_tasks():
    try:
        with open(TASK_FILE, 'r') as f:
            return json.load(f)
    except:
        return []

def save_tasks(tasks):
    with open(TASK_FILE, 'w') as f:
        json.dump(tasks, f, indent=4)

# Routes

# Teacher portal (announcements)
@teacher_bp.route('/teachers1')
def teacher_portal():
    return render_template('teachers1.html')

# Add Task
@teacher_bp.route('/add1', methods=['GET', 'POST'])
def add_task():
    if request.method == 'POST':
        task = {
            'title': request.form['title'],
            'description': request.form['description'],
            'due_date': request.form['due_date'],
            'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'status': 'Pending',
            'submission': None
        }
        tasks = load_tasks()
        tasks.append(task)
        save_tasks(tasks)
        return redirect(url_for('teacher.view_tasks'))
    return render_template('add_task.html')

# View Tasks
@teacher_bp.route('/view')
def view_tasks():
    tasks = load_tasks()
    return render_template('view_tasks.html', tasks=tasks)

# View Progress
@teacher_bp.route('/progress')
def view_progress():
    tasks = load_tasks()
    return render_template('view_progress.html', tasks=tasks)
