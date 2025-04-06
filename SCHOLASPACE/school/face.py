import cv2
import os
from flask import Flask, request, render_template,Blueprint
from datetime import date, datetime
import numpy as np
from sklearn.neighbors import KNeighborsClassifier
import pandas as pd
import joblib


face_bp = Blueprint('face', __name__ , template_folder='templates')

# Number of images to take for each user
nimgs = 20

# Saving Date today in 2 different formats
datetoday = date.today().strftime("%m_%d_%y")

# Initializing VideoCapture object to access WebCam
face_detector = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

# Ensure necessary directories exist
if not os.path.isdir('Attendance'):
    os.makedirs('Attendance')
if not os.path.isdir('static'):
    os.makedirs('static')
if not os.path.isdir('static/faces'):
    os.makedirs('static/faces')
if f'Attendance-{datetoday}.csv' not in os.listdir('Attendance'):
    with open(f'Attendance/Attendance-{datetoday}.csv', 'w') as f:
        f.write('Name,Roll,Time')

# Get the total number of registered users
def totalreg():
    return len(os.listdir('static/faces'))

# Extract faces from an image
def extract_faces(img):
    if img is not None:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        face_points = face_detector.detectMultiScale(gray, 1.2, 5, minSize=(20, 20))
        return face_points
    else:
        return []

# Identify face using pre-trained model
def identify_face(facearray):
    model = joblib.load('static/face_recognition_model.pkl')
    return model.predict(facearray)

# Train the model on all available faces in the 'faces' folder
def train_model():
    faces = []
    labels = []
    userlist = os.listdir('static/faces')
    for user in userlist:
        for imgname in os.listdir(f'static/faces/{user}'):
            img = cv2.imread(f'static/faces/{user}/{imgname}')
            resized_face = cv2.resize(img, (50, 50))
            faces.append(resized_face.ravel())
            labels.append(user)
    faces = np.array(faces)
    knn = KNeighborsClassifier(n_neighbors=5)
    knn.fit(faces, labels)
    joblib.dump(knn, 'static/face_recognition_model.pkl')

# Extract attendance information from today's attendance file
def extract_attendance():
    df = pd.read_csv(f'Attendance/Attendance-{datetoday}.csv')
    names = df['Name']
    rolls = df['Roll']
    times = df['Time']
    l = len(df)
    return names, rolls, times, l

# Add attendance record for a specific user
def add_attendance(name):
    username, userid = name.split('_')
    current_time = datetime.now().strftime("%H:%M:%S")

    df = pd.read_csv(f'Attendance/Attendance-{datetoday}.csv')
    if int(userid) not in list(df['Roll']):
        with open(f'Attendance/Attendance-{datetoday}.csv', 'a') as f:
            f.write(f'\n{username},{userid},{current_time}')

################## ROUTING FUNCTIONS #######################
####### for Face Recognition based Attendance System #######

# Main page
@face_bp.route('/home')
def home():
    names, rolls, times, l = extract_attendance()
    return render_template('face.html', names=names, rolls=rolls, times=times, l=l, totalreg=totalreg())

# Face recognition and attendance functionality
@face_bp.route('/start', methods=['GET'])
def start():
    if 'face_recognition_model.pkl' not in os.listdir('static'):
        return render_template('face.html', totalreg=totalreg(), mess='No trained model found in static folder. Add a new face to continue.')

    cap = cv2.VideoCapture(0)
    try:
        while True:
            ret, frame = cap.read()
            if ret and len(extract_faces(frame)) > 0:
                (x, y, w, h) = extract_faces(frame)[0]
                cv2.rectangle(frame, (x, y), (x+w, y+h), (86, 32, 251), 1)
                cv2.rectangle(frame, (x, y), (x+w, y-40), (86, 32, 251), -1)
                face = cv2.resize(frame[y:y+h, x:x+w], (50, 50))
                identified_person = identify_face(face.reshape(1, -1))[0]
                add_attendance(identified_person)
                cv2.putText(frame, f'{identified_person}', (x+5, y-5), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            cv2.imshow('Attendance', frame)
            if cv2.waitKey(1) == 27:
                break
    finally:
        # Ensure the webcam and all windows are properly closed after attendance is taken
        cap.release()
        cv2.destroyAllWindows()

    names, rolls, times, l = extract_attendance()
    return render_template('face.html', names=names, rolls=rolls, times=times, l=l, totalreg=totalreg())

# Add a new user to the system
@face_bp.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        # Get new username and userid from form safely
        newusername = request.form.get('newusername', None)
        newuserid = request.form.get('newuserid', None)

        if newusername is None or newuserid is None:
            return render_template('face.html', totalreg=totalreg(), mess='Username and UserID are required.')

        userimagefolder = f'static/faces/{newusername}_{str(newuserid)}'
        if not os.path.isdir(userimagefolder):
            os.makedirs(userimagefolder)
        cap = cv2.VideoCapture(0)
        try:
            i = 0
            while i < nimgs:
                ret, frame = cap.read()
                if ret and len(extract_faces(frame)) > 0:
                    (x, y, w, h) = extract_faces(frame)[0]
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
                    face = frame[y:y+h, x:x+w]
                    cv2.imwrite(f'{userimagefolder}/{i}.jpg', face)
                    i += 1
                cv2.imshow('Adding new user', frame)
                if cv2.waitKey(1) == 27:
                    break
        finally:
            # Ensure the webcam and all windows are properly closed after adding the user
            cap.release()
            cv2.destroyAllWindows()
        train_model()
    
    names, rolls, times, l = extract_attendance()
    return render_template('face.html', names=names, rolls=rolls, times=times, l=l, totalreg=totalreg())


