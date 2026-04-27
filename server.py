from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import subprocess
import os
import json
import threading

app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DASHBOARD_DIR = os.path.join(BASE_DIR, 'dashboard')

def run_command(command):
    try:
        # Run the command and capture output
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding='cp949',
            errors='replace'
        )
        output, _ = process.communicate()
        return output, process.returncode
    except Exception as e:
        return str(e), 1

@app.route('/')
def index():
    return send_from_directory(DASHBOARD_DIR, 'index.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory(DASHBOARD_DIR, path)

@app.route('/api/connect', methods=['POST'])
def api_connect():
    data = request.json
    db_type = data.get('type', 'source')
    # In a real app, we would update the config file with the data from frontend
    # For now, we run the existing connect command
    command = f"python main.py connect --type {db_type}"
    output, code = run_command(command)
    return jsonify({"output": output, "status": "success" if code == 0 else "error"})

@app.route('/api/extract-ddl', methods=['POST'])
def api_extract():
    command = "python main.py extract-ddl"
    output, code = run_command(command)
    return jsonify({"output": output, "status": "success" if code == 0 else "error"})

@app.route('/api/export', methods=['POST'])
def api_export():
    data = request.json or {}
    command = "python main.py export"
    
    if data.get("method"):
        command += f" --method {data['method']}"
    if data.get("mode"):
        command += f" --mode {data['mode']}"
    if data.get("targets"):
        command += f' --targets "{data["targets"]}"'
    if data.get("directory"):
        command += f' --directory "{data["directory"]}"'
    if data.get("dumpfile"):
        command += f' --dumpfile "{data["dumpfile"]}"'
    if data.get("logfile"):
        command += f' --logfile "{data["logfile"]}"'
    if data.get("parallel"):
        command += f" --parallel {data['parallel']}"
    if data.get("compression"):
        command += f" --compression {data['compression']}"
    if data.get("schemas"): # fallback
        command += f' --schemas "{data["schemas"]}"'
    if "consistent" in data:
        command += " --consistent" if data["consistent"] else " --no-consistent"
    if data.get("content"):
        command += f" --content {data['content']}"
    if data.get("exclude"):
        command += f' --exclude "{data["exclude"]}"'
    if data.get("estimate_only"):
        command += " --estimate-only"
        
    output, code = run_command(command)
    return jsonify({"output": output, "status": "success" if code == 0 else "error"})

@app.route('/api/setup-target', methods=['POST'])
def api_setup():
    command = "python main.py setup-target"
    output, code = run_command(command)
    return jsonify({"output": output, "status": "success" if code == 0 else "error"})

@app.route('/api/import', methods=['POST'])
def api_import():
    command = "python main.py import"
    output, code = run_command(command)
    return jsonify({"output": output, "status": "success" if code == 0 else "error"})

@app.route('/api/compare', methods=['POST'])
def api_compare():
    command = "python main.py compare"
    output, code = run_command(command)
    return jsonify({"output": output, "status": "success" if code == 0 else "error"})

if __name__ == '__main__':
    app.run(port=8000, debug=True)
