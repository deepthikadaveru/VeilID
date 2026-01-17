import hashlib
import numpy as np

SALT = "VeilID_Secure_Salt_2026"

def quantize(embedding, decimals=2):
    emb = embedding / np.linalg.norm(embedding)
    return np.round(emb, decimals)

def hash_embedding(embedding: np.ndarray) -> str:
    q = quantize(embedding)
    salted = q.tobytes() + SALT.encode()
    return hashlib.sha256(salted).hexdigest()

def similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
