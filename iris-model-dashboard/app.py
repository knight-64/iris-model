from pathlib import Path
import numpy as np
from flask import Flask, jsonify, render_template, request
from tensorflow.keras.models import load_model

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "my_model.h5"

# Assumes your model was trained with the standard Iris label encoding:
# 0 = setosa, 1 = versicolor, 2 = virginica.
# Change this order if your training labels used a different encoding.
CLASS_NAMES = ["Iris setosa", "Iris versicolor", "Iris virginica"]
FEATURE_NAMES = [
    "Sepal length (cm)",
    "Sepal width (cm)",
    "Petal length (cm)",
    "Petal width (cm)",
]

app = Flask(__name__)
model = load_model(MODEL_PATH, compile=False)

# Fail early if a different model is accidentally placed in this project.
if tuple(model.input_shape[1:]) != (4,):
    raise ValueError(f"Expected model input shape (None, 4), got {model.input_shape}")
if int(model.output_shape[-1]) != len(CLASS_NAMES):
    raise ValueError(f"Expected {len(CLASS_NAMES)} output classes, got {model.output_shape}")


@app.get("/")
def home():
    return render_template("index.html")


@app.get("/api/health")
def health():
    return jsonify({"status": "ok", "model_loaded": True, "input_features": FEATURE_NAMES, "classes": CLASS_NAMES})


@app.post("/api/predict")
def predict():
    payload = request.get_json(silent=True) or {}
    try:
        values = [float(payload[name]) for name in ("sepal_length", "sepal_width", "petal_length", "petal_width")]
    except (KeyError, TypeError, ValueError):
        return jsonify({"error": "Enter all four measurements as valid numbers."}), 400

    if not np.all(np.isfinite(values)):
        return jsonify({"error": "Measurements must be finite numbers."}), 400
    if any(value <= 0 or value > 10 for value in values):
        return jsonify({"error": "Enter realistic Iris measurements between 0 and 10 cm."}), 400

    # The model receives the four measurements in the exact order above.
    # If you scaled/standardized features during training, apply that same
    # fitted preprocessing transformation here before calling predict().
    probabilities = np.asarray(model.predict(np.array([values], dtype=np.float32), verbose=0))[0]
    probabilities = np.clip(probabilities.astype(float), 0.0, 1.0)
    total = float(probabilities.sum())
    if total > 0:
        probabilities = probabilities / total

    winner = int(np.argmax(probabilities))
    return jsonify({
        "prediction": CLASS_NAMES[winner],
        "class_index": winner,
        "confidence": round(float(probabilities[winner]) * 100, 2),
        "probabilities": [
            {"class_name": CLASS_NAMES[i], "probability": round(float(probabilities[i]) * 100, 2)}
            for i in range(len(CLASS_NAMES))
        ],
        "measurements": dict(zip(["sepal_length", "sepal_width", "petal_length", "petal_width"], values)),
    })


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
