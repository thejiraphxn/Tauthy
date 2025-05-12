import os
import pandas as pd
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

def clean_text(text):
    """Basic text cleaning: lowercase and strip."""
    return text.strip().lower()

def train_model(csv_path, model_output_path):
    """Train AI Text Classifier and save model."""

    df = pd.read_csv(csv_path)

    if 'text' not in df.columns or 'label' not in df.columns:
        raise ValueError("CSV must contain 'text' and 'label' columns.")

    df['text'] = df['text'].apply(clean_text)

    X_train, X_test, y_train, y_test = train_test_split(
        df['text'], df['label'], test_size=0.2, random_state=42
    )

    vectorizer = TfidfVectorizer()
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)

    model = LogisticRegression()
    model.fit(X_train_vec, y_train)

    y_pred = model.predict(X_test_vec)
    acc = accuracy_score(y_test, y_pred)
    print(f"Validation Accuracy: {acc*100:.2f}%")

    model_data = {
        'vectorizer': vectorizer,
        'model': model
    }
    joblib.dump(model_data, model_output_path)
    print(f"Model saved to: {model_output_path}")

    # ✅ 8. Report number of training rows
    print(f"Total training samples used: {X_train_vec.shape[0]}")
    print(f"Total dataset size (before split): {len(df)}")
    train_label_counts = pd.Series(y_train).value_counts()
    test_label_counts = pd.Series(y_test).value_counts()

    print("Training label distribution:")
    for label in ['ai', 'human']:
        count = train_label_counts.get(label, 0)
        print(f"   - {label.upper()}: {count} samples")

    print("Testing label distribution:")
    for label in ['ai', 'human']:
        count = test_label_counts.get(label, 0)
        print(f"   - {label.upper()}: {count} samples")


if __name__ == "__main__":
    ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    CSV_PATH = os.path.join(ROOT_DIR, "data", "train_cleaned.csv")
    MODEL_PATH = os.path.join(ROOT_DIR, "models", "ai_model.pkl")

    train_model(csv_path=CSV_PATH, model_output_path=MODEL_PATH)