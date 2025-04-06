import os
from flask import Flask, render_template
from school.voice import voice_bp
from school.doubt import doubt_bp
from school.task import teacher_bp
from school.rhyme import rhyme_bp
from school.face import face_bp
from school.stu import stu_bp
from extension import db, login_manager, socketio

app = Flask(__name__)
app.config['SECRET_KEY'] = "my-secrets"
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///video-meeting.db"
app.config['UPLOAD_FOLDER'] = 'uploads'
app.secret_key = 'supersecretkey'

# Create uploads folder if not exists
if not os.path.exists('uploads'):
    os.makedirs('uploads')

# Initialize extensions with the app
db.init_app(app)
login_manager.init_app(app)
socketio.init_app(app)

app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'doc', 'docx', 'ppt', 'pptx', 'xls', 'xlsx'}
login_manager.login_view = "meet.login"

# Importing and registering blueprints
from school.meet import meet_bp  # Import after initializing extensions to avoid circular import
app.register_blueprint(voice_bp)
app.register_blueprint(doubt_bp)
app.register_blueprint(rhyme_bp)
app.register_blueprint(face_bp)
app.register_blueprint(meet_bp)
app.register_blueprint(teacher_bp)
app.register_blueprint(stu_bp, url_prefix='/stu')

# Create tables within application context
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/no')
def nope():
    return render_template('notes.html')


@app.route('/student')
def student():
    return render_template('student.html')

@app.route('/rhyme')
def kids():
    return render_template('notes.html')

@app.route('/teachers')
def teachers():
    return render_template('teacher.html')

@app.route('/teachers/teachers1')
def teacher_portal():
    return render_template('teachers1.html')

@app.route('/voice/voice1')
def voice_bot():
    return render_template('voice.html')

@app.route('/doubt')
def doubt():
    return render_template('doubt.html')

# Route to prevent favicon 404 error
@app.route('/favicon.ico')
def favicon():
    return "", 204  # Return a blank response with HTTP status 204 (No Content)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
