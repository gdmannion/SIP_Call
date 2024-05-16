# app.py

from flask import Flask, request, jsonify, render_template, session, redirect
import requests
import json
from requests.auth import HTTPDigestAuth
from call_functions import make_call

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Set a secret key for session management

# Define global variables for username, password, and IP address
cam_user = ""
cam_pass = ""
ip_address = ""

# Function to terminate a call
def terminate_call(ip_address, cam_user, cam_pass, call_id):
    auth = HTTPDigestAuth(cam_user, cam_pass)
    url = f"http://{ip_address}/vapix/call"

    payload = json.dumps({
        "axcall:TerminateCall": {
            "CallId": call_id
        }
    })

    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.post(url, auth=auth, headers=headers, data=payload)
    return response

# Route to index.html
@app.route('/')
def index():
    return render_template('index.html')

# Route to make a call
@app.route('/make_call', methods=['POST'])
def make_call_route():
    global cam_user, cam_pass, ip_address
    ip_address = request.form.get('ip_address')
    cam_user = request.form.get('username')
    cam_pass = request.form.get('password')
    destination = request.form.get('destination')  # Retrieve destination number
    
    response = make_call(ip_address, cam_user, cam_pass, destination)

    if response.status_code == 200:
        try:
            call_id = response.json()['CallId']
            # Store the CallId in session so that it can be accessed later
            session['call_id'] = call_id
            return redirect('/call_status')
        except KeyError:
            return jsonify({'error': 'Failed to retrieve CallId from response'}), 500
    else:
        return jsonify({'error': 'Failed to make call'}), response.status_code

# Route to get the call status
@app.route('/call_status')
def call_status():
    global cam_user, cam_pass, ip_address
    call_id = session.get('call_id')  # Retrieve CallId from session
    
    auth = HTTPDigestAuth(cam_user, cam_pass)
    url = f"http://{ip_address}/vapix/call"

    payload = json.dumps({
        "axcall:GetCallStatus": {
            "CallId": call_id
        }
    })

    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.post(url, auth=auth, headers=headers, data=payload)

    if response.status_code == 200:
        call_status = response.json()
        return render_template('call_status.html', call_status=call_status)
    else:
        return jsonify({'error': 'Failed to get call status'}), response.status_code

# Route to terminate the call
@app.route('/terminate_call', methods=['POST'])
def terminate_call_route():
    global cam_user, cam_pass, ip_address
    call_id = session.get('call_id')  # Retrieve CallId from session

    response = terminate_call(ip_address, cam_user, cam_pass, call_id)

    if response.status_code == 200:
        return jsonify({'success': 'Call terminated successfully'}), 200
    else:
        return jsonify({'error': 'Failed to terminate call'}), response.status_code

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
