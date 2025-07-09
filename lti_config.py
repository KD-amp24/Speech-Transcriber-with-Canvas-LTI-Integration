from flask import Flask, request, redirect, session, jsonify
from pylti1p3.contrib.flask import FlaskRequest
from pylti1p3.tool_config import ToolConfJsonFile
from pylti1p3.session import SessionDataStorage
from pylti1p3.message_launch import MessageLaunch

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a strong secret key

# Load tool configuration
tool_config = ToolConfJsonFile('tool_config_backend.json')
launch_data_storage = SessionDataStorage(session)

@app.route('/lti/login', methods=['GET'])
def login():
    flask_request = FlaskRequest(request)
    oidc_login = flask_request.get_oidc_login(tool_config)
    return oidc_login.enable_check_cookies() \
        .redirect(flask_request.get_param('target_link_uri'))

@app.route('/lti/launch', methods=['POST'])
def launch():
    flask_request = FlaskRequest(request)
    message_launch = MessageLaunch(flask_request, tool_config, launch_data_storage)
    launch_data = message_launch.get_launch_data()
    session['launch_id'] = message_launch.get_launch_id()
    return jsonify({
        "message": "LTI Launch Successful!",
        "user": launch_data.get("name"),
        "roles": launch_data.get("https://purl.imsglobal.org/spec/lti/claim/roles"),
        "context": launch_data.get("https://purl.imsglobal.org/spec/lti/claim/context")
    })

@app.route('/lti/session', methods=['GET'])
def get_session():
    if 'launch_id' not in session:
        return jsonify({"error": "No active launch session"}), 401
    return jsonify({"launch_id": session['launch_id']})

if __name__ == '__main__':
    app.run(debug=True)
