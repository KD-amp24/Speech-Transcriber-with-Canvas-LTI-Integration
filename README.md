# 🧠 Speech Transcriber with Canvas LTI Integration

This project provides a Flask-based web app for transcribing and evaluating oral responses using OpenAI’s Whisper model (via FasterWhisper). It integrates seamlessly with Canvas LMS via LTI 1.3.

## 🔍 Features

- Upload or record speech from a browser
- Transcribe using FasterWhisper (OpenAI)
- Evaluate responses using a keyword-based rubric
- LTI 1.3 Launch from Canvas
- Secure, rate-limited Flask backend

## 🧪 Demo

[![](https://img.shields.io/badge/Live%20Demo-Available-brightgreen)](https://your-live-link-here-if-any)

## ⚙️ Technologies Used

- Python + Flask
- OpenAI Whisper / FasterWhisper
- JavaScript, HTML5, CSS3
- LTI 1.3 via `pylti1p3`
- Canvas LMS integration

## 📂 Project Structure

```
.
├── app.py
├── whisper_eval.py
├── lti_config.py
├── tool_config.json
├── tool_config_backend.json
├── templates/
│   └── index.html
├── static/
│   ├── css/style.css
│   ├── js/main.js
│   └── img/spinner.gif
├── keys/
│   └── jwk_public.json
├── requirements.txt
└── README.md
```

## 🚀 Getting Started

### 🔧 Requirements

- Python 3.8+
- `ffmpeg` (for audio processing)

### 🔌 Installation

```bash
git clone https://github.com/KD-amp24/Speech-Transcriber-with-Canvas-LTI-Integration.git
cd Speech-Transcriber-with-Canvas-LTI-Integration
python -m venv venv
source venv/bin/activate  # or .\venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### ▶️ Running Locally

```bash
python app.py
```

Then go to `http://localhost:5000` to use the app.

## 🧪 Testing LTI Integration

- Register the tool in Canvas Developer Keys
- Use `tool_config.json` for configuration
- Use Ngrok or similar for tunneling (e.g. `https://yourapp.ngrok.io`)

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first.

## 👨‍🏫 Supervision & Acknowledgment

Developed by **Kwadwo Amponsah Ampofo**, graduate student at Jackson State University  
Supervised by **Dr. Wei Zheng**, Department of Civil Engineering  
Powered by SYSTRAN's FASTER Whisper

## 📜 License

[MIT](LICENSE)
