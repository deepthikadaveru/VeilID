import sys
import os
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_DIR)

from flask import Flask, request, jsonify, render_template
import json
import base64
import numpy as np
import cv2
from deepface import DeepFace
from security.hasher import hash_embedding, quantize, similarity

app = Flask(__name__)
DB_FILE = "hashes.json"

def load_db():
    if not os.path.exists(DB_FILE):
        return {}
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

def base64_to_image(base64_string):
    header, encoded = base64_string.split(",", 1)
    img_bytes = base64.b64decode(encoded)
    img_array = np.frombuffer(img_bytes, dtype=np.uint8)
    image = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
    return image

def get_face_embedding(image):
    result = DeepFace.represent(img_path=image, model_name="Facenet", enforce_detection=True)
    return np.array(result[0]["embedding"])

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/register", methods=["POST"])
def register():
    data = request.json
    student_id = data["student_id"]
    image_data = data["image"]

    image = base64_to_image(image_data)
    embedding = get_face_embedding(image)

    q = quantize(embedding)
    face_hash = hash_embedding(embedding)

    db = load_db()
    db[student_id] = {
        "hash": face_hash,
        "signature": q.tolist()
    }
    save_db(db)

    return jsonify({
        "status": "Identity Registered",
        "privacy": "Only quantized templates and cryptographic hashes stored. No face images."
    })

@app.route("/verify", methods=["POST"])
def verify():
    data = request.json
    student_id = data["student_id"]
    image_data = data["image"]

    if not os.path.exists(DB_FILE):
        return jsonify({"status": "No identities registered"})

    db = load_db()
    if student_id not in db:
        return jsonify({"status": "Unknown Identity"})

    image = base64_to_image(image_data)
    embedding = get_face_embedding(image)
    q_new = quantize(embedding)

    stored_sig = np.array(db[student_id]["signature"])
    score = similarity(stored_sig, q_new)

    if score > 0.92:
        return jsonify({
            "status": "Verified — Attendance Marked",
            "similarity": float(score)
        })
    else:
        return jsonify({
            "status": "Verification Failed — Face Mismatch",
            "similarity": float(score)
        })

if __name__ == "__main__":
    app.run(debug=True)
