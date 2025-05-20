# intent_classifier.py

import pickle
import os

# Model ve vectorizer dosya yolları
MODEL_PATH = "intent_model.pkl"
VECTORIZER_PATH = "vectorizer.pkl"

# Model ve vectorizer'ı yükle
with open(MODEL_PATH, "rb") as f:
    classifier = pickle.load(f)

with open(VECTORIZER_PATH, "rb") as f:
    vectorizer = pickle.load(f)

def predict_intent(command):
    """Verilen komutun intent'ini tahmin eder."""
    command = command.lower().strip()
    vector = vectorizer.transform([command])
    intent = classifier.predict(vector)[0]
    return intent
