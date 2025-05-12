import joblib
import os
import re
import string
from sklearn.pipeline import Pipeline
from pythainlp.tokenize import word_tokenize
from pythainlp.util import normalize
from pythainlp.corpus.common import thai_stopwords

THAI_STOPWORDS = set(thai_stopwords())

model_path = "models/ai_model.pkl"
if not os.path.exists(model_path):
    raise FileNotFoundError(f"❌ Model file not found: {model_path}")

model_data = joblib.load(model_path)
vectorizer = model_data['vectorizer']
model = model_data['model']

def is_thai(text: str) -> bool:
    return any('\u0E00' <= ch <= '\u0E7F' for ch in text)

def clean_text(text: str) -> str:
    text = normalize(text.strip())
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"\d+", "", text)
    text = re.sub(r"[^\w\s]", "", text)
    text = re.sub(r"\s+", " ", text)
    text = text.lower().strip()

    if is_thai(text):
        tokens = word_tokenize(text, engine="newmm")
        tokens = [t for t in tokens if t not in THAI_STOPWORDS and len(t.strip()) > 1]
    else:
        tokens = text.split()
        tokens = [t for t in tokens if t not in string.punctuation]

    return " ".join(tokens)

def predict_text(text: str):
    cleaned = clean_text(text)

    if len(cleaned.split()) < 5:
        return {
            "label": "undecided",
            "confidence": 0.0,
            "details": {}
        }

    X = vectorizer.transform([cleaned])
    raw_probs = model.predict_proba(X)[0]
    classes = model.classes_

    # Normalize and convert to percentage
    total = sum(raw_probs)
    probs = [p / total for p in raw_probs]
    results_percent = {cls: round(p * 100, 2) for cls, p in zip(classes, probs)}

    # Adjust total to exactly 100%
    diff = 100.0 - sum(results_percent.values())
    top_cls = max(results_percent, key=results_percent.get)
    results_percent[top_cls] = round(results_percent[top_cls] + diff, 2)

    top_label = max(results_percent, key=results_percent.get)
    top_conf = results_percent[top_label]

    return {
        "label": top_label,
        "confidence": top_conf,
        "details": results_percent
    }
