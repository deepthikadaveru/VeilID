import sys
import os

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_DIR)

import cv2
import requests
from deepface import DeepFace
from security.hasher import hash_embedding

SERVER_URL = "http://127.0.0.1:5000"
def capture_face():
    cam = cv2.VideoCapture(0)

    if not cam.isOpened():
        print("Camera not opening. Trying alternate index...")
        cam = cv2.VideoCapture(1)

    print("Camera ready. Press ENTER in the video window to capture.")

    cv2.namedWindow("VeilID Capture", cv2.WINDOW_NORMAL)

    while True:
        ret, frame = cam.read()
        if not ret:
            continue

        cv2.imshow("VeilID Capture", frame)

        key = cv2.waitKey(30) & 0xFF
        if key == 13:  # ENTER
            cv2.imwrite("temp_face.jpg", frame)
            print("Face captured.")
            break

    cam.release()
    cv2.destroyAllWindows()
    return "temp_face.jpg"


def generate_embedding(image_path):
    result = DeepFace.represent(img_path=image_path, model_name="Facenet", enforce_detection=True)
    return result[0]["embedding"]

def register(student_id):
    image = capture_face()
    embedding = generate_embedding(image)
    face_hash = hash_embedding(embedding)

    response = requests.post(f"{SERVER_URL}/register", json={
        "student_id": student_id,
        "hash": face_hash
    })

    print(response.json())

def verify(student_id):
    image = capture_face()
    embedding = generate_embedding(image)
    face_hash = hash_embedding(embedding)

    response = requests.post(f"{SERVER_URL}/verify", json={
        "student_id": student_id,
        "hash": face_hash
    })

    print(response.json())

if __name__ == "__main__":
    choice = input("1. Register\n2. Mark Attendance\nChoose: ")

    sid = input("Enter Student ID: ")

    if choice == "1":
        register(sid)
    else:
        verify(sid)
