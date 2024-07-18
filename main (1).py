import face_recognition
import cv2
from datetime import datetime
import csv
import os

# Load the video capture
video_capture = cv2.VideoCapture(0)

# Define paths to the images
images_folder = "/Users/prahasithtr/Desktop/Images"
names = ["prahasith", "pragya"]
known_face_encodings = []
known_face_names = []

# Load and encode images from each subfolder
for name in names:
    folder_path = os.path.join(images_folder, name)
    image_paths = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith(('.jpg', '.jpeg', '.png'))]
    for image_path in image_paths:
        image = face_recognition.load_image_file(image_path)
        encoding = face_recognition.face_encodings(image)[0]  # Assuming there's only one face in each image
        known_face_encodings.append(encoding)
        known_face_names.append(name)

# Initialize attendance record
students_attendance = {name: {'Time In': None, 'Time Out': None} for name in known_face_names}

# Record the start time of the video
start_time = datetime.now()

# Loop over each frame in the video
while True:
    ret, frame = video_capture.read()
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

    face_locations = face_recognition.face_locations(rgb_small_frame)
    face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

    face_names = []
    for face_encoding in face_encodings:
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
        name = "Unknown"

        if True in matches:
            first_match_index = matches.index(True)
            name = known_face_names[first_match_index]

        face_names.append(name)
        if name in students_attendance and students_attendance[name]['Time In'] is None:
            students_attendance[name]['Time In'] = datetime.now().strftime("%H:%M:%S")

    for (top, right, bottom, left), name in zip(face_locations, face_names):
        top *= 4
        right *= 4
        bottom *= 4
        left *= 4
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

    cv2.imshow('Video', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        end_time = datetime.now().strftime("%H:%M:%S")
        for student in students_attendance:
            if students_attendance[student]['Time In'] is not None:
                students_attendance[student]['Time Out'] = end_time
        break

video_capture.release()
cv2.destroyAllWindows()

# Write to CSV file
now = datetime.now()
current_date = now.strftime("%Y-%m-%d")
csv_file_name = current_date + '.csv'
with open(csv_file_name, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['Name', 'UCID', 'Time In', 'Time Out'])
    for name, times in students_attendance.items():
        ucid = "12345678" if name == "prahasith" else "87654321" if name == "pragya" else ""
        writer.writerow([name, ucid, times['Time In'], times['Time Out']])
