const form = document.getElementById('prediction-form');
const predictButton = document.getElementById('predict-btn');
const errorBox = document.getElementById('form-error');
const emptyState = document.getElementById('empty-state');
const result = document.getElementById('prediction-result');
const fields = ['sepal_length', 'sepal_width', 'petal_length', 'petal_width'];

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  errorBox.textContent = '';
  const values = {};
  for (const name of fields) {
    const input = document.getElementById(name);
    const value = Number(input.value);
    if (!input.value || !Number.isFinite(value) || value <= 0 || value > 10) {
      errorBox.textContent = 'Please enter all four measurements between 0 and 10 cm.';
      input.focus();
      return;
    }
    values[name] = value;
  }

  predictButton.disabled = true;
  predictButton.querySelector('span').textContent = 'Analyzing…';
  predictButton.querySelector('b').textContent = '···';
  try {
    const response = await fetch('/api/predict', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(values)
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'Prediction failed.');
    showPrediction(data);
  } catch (error) {
    errorBox.textContent = error.message || 'Could not connect to the prediction server.';
  } finally {
    predictButton.disabled = false;
    predictButton.querySelector('span').textContent = 'Predict species';
    predictButton.querySelector('b').textContent = '→';
  }
});

function showPrediction(data) {
  emptyState.classList.add('hidden');
  result.classList.remove('hidden');
  document.getElementById('winner-name').textContent = data.prediction;
  document.getElementById('confidence-value').textContent = `${data.confidence.toFixed(2)}%`;
  requestAnimationFrame(() => {
    document.getElementById('confidence-fill').style.width = `${data.confidence}%`;
  });
  const list = document.getElementById('probability-list');
  list.innerHTML = '';
  data.probabilities.forEach(item => {
    const row = document.createElement('div');
    row.className = 'probability-row';
    const meta = document.createElement('div');
    meta.className = 'probability-meta';
    const name = document.createElement('span');
    name.textContent = item.class_name;
    const value = document.createElement('b');
    value.textContent = `${item.probability.toFixed(2)}%`;
    meta.append(name, value);
    const track = document.createElement('div');
    track.className = 'probability-track';
    const fill = document.createElement('span');
    fill.style.width = `${item.probability}%`;
    track.append(fill);
    row.append(meta, track);
    list.append(row);
  });
}

document.getElementById('reset-btn').addEventListener('click', () => {
  form.reset();
  errorBox.textContent = '';
  document.getElementById('confidence-fill').style.width = '0%';
  result.classList.add('hidden');
  emptyState.classList.remove('hidden');
});
