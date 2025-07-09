from flask import Flask, request, jsonify, send_file, redirect, session, render_template_string, url_for
from pylti1p3.tool_config import ToolConfJsonFile
from pylti1p3.contrib.flask import FlaskRequest, FlaskCacheDataStorage, FlaskMessageLaunch, FlaskSessionService, FlaskCookieService
from pylti1p3.exception import LtiException
from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from functools import wraps
from werkzeug.utils import secure_filename
from pylti1p3.oidc_login import OIDCLogin
import os
import json
import tempfile

from whisper_eval import transcribe_and_evaluate

print("Working directory:", os.getcwd())

app = Flask(__name__)
app.secret_key = 'your_super_secret_key'

flask_cache = Cache(app, config={'CACHE_TYPE': 'SimpleCache'})
cache = FlaskCacheDataStorage(flask_cache)

limiter = Limiter(get_remote_address, app=app, default_limits=["10 per minute"])

app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    SESSION_COOKIE_SECURE=False,
    MAX_CONTENT_LENGTH=10 * 1024 * 1024
)

ALLOWED_EXTENSIONS = {'wav', 'mp3', 'm4a', 'mp4', 'flac', 'webm'}
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

LTI_CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'tool_config.json')
LTI_KEYS_PATH = os.path.join(os.path.dirname(__file__), 'keys')
LTI_ISSUER = "https://canvas.instructure.com"

tool_config = ToolConfJsonFile("tool_config_backend.json")

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def lti_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'launch_id' not in session:
            return redirect(url_for('lti_login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route("/lti/login", methods=["GET"])
def lti_login():
    try:
        flask_request = FlaskRequest(request)
        session_service = FlaskSessionService(flask_request)
        cookie_service = FlaskCookieService(flask_request)
        oidc_login = OIDCLogin(flask_request, tool_config, session_service, cookie_service)
        return oidc_login.redirect(flask_request)
    except Exception as e:
        return f"OIDC login error: {e}", 400

@app.route("/lti/launch", methods=["POST"])
def lti_launch():
    try:
        flask_request = FlaskRequest(request)
        message_launch = FlaskMessageLaunch(flask_request, tool_config, cache).verify()
        session['launch_id'] = message_launch.get_launch_id()
        user_info = message_launch.get_launch_data().get("https://purl.imsglobal.org/spec/lti/claim/custom", {})
        return f"✅ LTI Launch Success! Hello {user_info.get('user_id', 'student')}."
    except LtiException as e:
        return f"LTI Launch error: {e}", 400

@app.route("/keys", methods=["GET"])
def jwks():
    jwk_file = os.path.join(LTI_KEYS_PATH, "jwks.json")
    if os.path.exists(jwk_file):
        with open(jwk_file, "r") as f:
            jwks_data = json.load(f)
        return jsonify(jwks_data)
    else:
        return jsonify({"error": "JWKS not found"}), 404

@app.route("/tool_config.json", methods=["GET"])
def serve_tool_config():
    return send_file("tool_config.json", mimetype="application/json")

@app.route("/")
def index():
    return "🎙️ Oral Response Evaluator is running!"

@limiter.limit("3 per minute")
@app.route("/transcribe", methods=["POST"])
def transcribe():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "Invalid file type"}), 400

    filename = secure_filename(file.filename)
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(file_path)

    try:
        result = transcribe_and_evaluate(file_path)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

UPLOAD_FORM = """
<!doctype html>
<html>
<head>
  <title>Upload or Record Audio</title>
  <style>
    body {
      font-family: Arial, sans-serif;
      background: #f5f5f5;
      display: flex;
      justify-content: center;
      align-items: center;
      height: 100vh;
      margin: 0;
    }
    .upload-container {
      background: white;
      padding: 30px;
      border-radius: 12px;
      box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
      text-align: center;
      max-width: 400px;
      width: 100%;
    }
    input[type="file"] {
      margin-bottom: 15px;
    }
    button, input[type="submit"] {
      padding: 10px 20px;
      margin: 10px;
      font-size: 16px;
      border: none;
      border-radius: 6px;
      background-color: #3498db;
      color: white;
      cursor: pointer;
    }
    button:disabled {
      background-color: #ccc;
    }
    #status {
      margin-top: 10px;
      color: #555;
    }
  </style>
</head>
<body>
<div class="upload-container">
  <h2>Upload or Record Audio</h2>
  <form method="post" enctype="multipart/form-data">
    <input type="file" name="audio_file" required><br>
    <input type="submit" value="Upload">
  </form>
  <hr>
  <h3>Or Record Now</h3>
  <button id="recordBtn">Start Recording</button>
  <button id="stopBtn" disabled>Stop Recording</button>
  <p id="status"></p>
  <form id="recordForm" method="post" enctype="multipart/form-data" style="display:none;">
    <input type="file" name="audio_file" id="recordedAudio">
    <input type="submit" value="Submit Recording">
  </form>
</div>
<script>
let mediaRecorder;
let chunks = [];

recordBtn.onclick = async () => {
  chunks = [];
  const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
  mediaRecorder = new MediaRecorder(stream);
  mediaRecorder.ondataavailable = e => chunks.push(e.data);
  mediaRecorder.onstop = () => {
    const blob = new Blob(chunks, { type: 'audio/webm' });
    const file = new File([blob], 'recording.webm', { type: 'audio/webm' });
    const dataTransfer = new DataTransfer();
    dataTransfer.items.add(file);
    recordedAudio.files = dataTransfer.files;
    recordForm.style.display = "block";
    status.innerText = "Recording ready. Click submit.";
  };
  mediaRecorder.start();
  recordBtn.disabled = true;
  stopBtn.disabled = false;
  status.innerText = "Recording...";
};

stopBtn.onclick = () => {
  mediaRecorder.stop();
  recordBtn.disabled = false;
  stopBtn.disabled = true;
};
</script>
</body>
</html>
"""

RESULTS_PAGE = """
<!doctype html>
<html>
<head>
  <title>Transcription Results</title>
  <style>
    body {
      font-family: Arial, sans-serif;
      background: #f3f4f6;
      margin: 0;
      padding: 40px 20px;
      display: flex;
      justify-content: center;
      align-items: flex-start;
      min-height: 100vh;
    }
    .container {
      background: white;
      border-radius: 12px;
      padding: 30px;
      max-width: 700px;
      width: 100%;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }
    h1, h2 {
      color: #2c3e50;
      margin-bottom: 15px;
    }
    p {
      background: #f0f0f0;
      padding: 15px;
      border-radius: 8px;
      font-family: 'Courier New', monospace;
      color: #333;
    }
    ul {
      list-style: none;
      padding-left: 0;
    }
    li {
      background: #eaf3ff;
      margin-bottom: 8px;
      padding: 10px;
      border-left: 5px solid #3498db;
      border-radius: 6px;
    }
    .score {
      font-weight: bold;
      color: #27ae60;
    }
    .button-link {
      display: inline-block;
      margin-top: 20px;
      padding: 10px 20px;
      background-color: #4CAF50;
      color: white;
      text-decoration: none;
      border-radius: 6px;
      transition: background-color 0.3s ease;
    }
    .button-link:hover {
      background-color: #45a049;
    }
    @media (max-width: 600px) {
      .container {
        padding: 20px;
      }
    }
  </style>
</head>
<body>
  <div class="container">
    <h1>📝 Transcription</h1>
    <p>{{ transcript }}</p>
    <h2>📊 Evaluation</h2>
    <ul>
      <li><strong>Word Count:</strong> {{ evaluation.word_count }}</li>
      <li><strong>Contains "important":</strong> {{ evaluation.contains_keyword }}</li>
      {% if evaluation.rubric_score is defined %}
      <li class="score">Rubric Score: {{ evaluation.rubric_score }} / {{ total_rubric }}</li>
      <li><strong>Feedback:</strong></li>
      <ul>
        {% for fb in evaluation.rubric_feedback %}
          <li>{{ fb }}</li>
        {% endfor %}
      </ul>
      {% endif %}
    </ul>
    <a class="button-link" href="{{ url_for('upload_audio') }}">⬅️ Upload Another</a>
  </div>
</body>
</html>
"""

@app.route("/upload", methods=["GET", "POST"])
def upload_audio():
    if request.method == "POST":
        if 'audio_file' not in request.files:
            return "No audio_file part", 400
        file = request.files['audio_file']
        filename = secure_filename(file.filename) if file.filename else 'recording.webm'
        if not allowed_file(filename):
            return "Invalid file type", 400
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as tmp:
            file.save(tmp.name)
            temp_path = tmp.name
        try:
            result = transcribe_and_evaluate(temp_path)
        finally:
            os.remove(temp_path)
        evaluation = result.get("evaluation", {})
        if "score" in evaluation and "feedback" in evaluation:
            evaluation["rubric_score"] = evaluation["score"]
            evaluation["rubric_feedback"] = evaluation["feedback"]
        return render_template_string(
            RESULTS_PAGE,
            transcript=result.get("transcript", ""),
            evaluation=evaluation,
            total_rubric=4
        )
    else:
        return UPLOAD_FORM

if __name__ == "__main__":
    app.run(debug=False, port=5000)
