# IrisAI — H5 model dashboard

A responsive Iris flower classification dashboard connected to the uploaded `my_model.h5` Keras model. Flask serves the frontend and exposes `/api/predict`; TensorFlow loads and runs the actual model.

## Run locally

Use Python 3.10–3.12 (recommended for broad TensorFlow wheel compatibility).

```bash
# Windows PowerShell
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:5000.

## Model assumptions to verify

The inspected H5 architecture accepts **4 numeric inputs** and produces **3 softmax outputs**. The UI labels the inputs as standard Iris measurements, in this order:

1. Sepal length (cm)
2. Sepal width (cm)
3. Petal length (cm)
4. Petal width (cm)

The output labels currently assume the common Iris encoding: index 0 = setosa, 1 = versicolor, 2 = virginica. Confirm that this matches the label encoder used during training; if not, update `CLASS_NAMES` in `app.py`.

**Preprocessing matters:** this app passes raw measurements directly to the model. If training used `StandardScaler`, normalization, or another preprocessing step, save that fitted transformer and apply it in `app.py` before `model.predict()`. The H5 file alone does not reveal the training feature names, class mapping, or preprocessing pipeline.

## API

- `GET /api/health` — checks that the model loaded and reports expected inputs/classes.
- `POST /api/predict` — JSON body with `sepal_length`, `sepal_width`, `petal_length`, `petal_width`; returns the predicted class and softmax probabilities.

This is a local development setup. For public deployment, use a Python hosting platform that supports TensorFlow and configure production serving, request limits, and resource sizing.
