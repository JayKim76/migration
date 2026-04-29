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
    
    command = f"python main.py connect --type {db_type}"
    
    if data.get("server_host"):
        command += f' --server-host "{data["server_host"]}"'
    if data.get("ssh_user"):
        command += f' --ssh-user "{data["ssh_user"]}"'
    if data.get("ssh_password"):
        command += f' --ssh-password "{data["ssh_password"]}"'
    if data.get("host"):
        command += f' --host "{data["host"]}"'
    if data.get("port"):
        command += f' --port {data["port"]}'
    if data.get("service_name"):
        command += f' --service-name "{data["service_name"]}"'
    if data.get("username"):
        command += f' --username "{data["username"]}"'
    if data.get("password"):
        command += f' --password "{data["password"]}"'
        
    output, code = run_command(command)
    return jsonify({"output": output, "status": "success" if code == 0 else "error"})

@app.route('/api/extract-ddl', methods=['POST'])
def api_extract():
    data = request.json or {}
    ddl_dir = data.get('ddl_dir')
    command = "python main.py extract-ddl"
    if ddl_dir:
        command += f' --ddl-dir "{ddl_dir}"'
        
    output, code = run_command(command)
    return jsonify({"output": output, "status": "success" if code == 0 else "error"})

def build_export_command(data):
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
        
    if data.get("estimate"): command += f" --estimate {data['estimate']}"
    if data.get("filesize"): command += f' --filesize "{data["filesize"]}"'
    if data.get("flashback_scn"): command += f' --flashback-scn "{data["flashback_scn"]}"'
    if data.get("flashback_time"): command += f' --flashback-time "{data["flashback_time"]}"'
    if data.get("include"): command += f' --include "{data["include"]}"'
    if data.get("network_link"): command += f' --network-link "{data["network_link"]}"'
    if data.get("query"): command += f' --query "{data["query"]}"'
    if data.get("remap_data"): command += f' --remap-data "{data["remap_data"]}"'
    if data.get("reuse_dumpfiles"): command += " --reuse-dumpfiles"
    if data.get("sample"): command += f' --sample "{data["sample"]}"'
    if data.get("version"): command += f' --version "{data["version"]}"'
    if data.get("cluster"): command += " --cluster"
    if data.get("encryption"): command += f" --encryption {data['encryption']}"
    if data.get("encryption_algorithm"): command += f" --encryption-algorithm {data['encryption_algorithm']}"
    if data.get("encryption_mode"): command += f" --encryption-mode {data['encryption_mode']}"
    if data.get("encryption_password"): command += f' --encryption-password "{data["encryption_password"]}"'
    if data.get("job_name"): command += f' --job-name "{data["job_name"]}"'

    # exp-only
    if "grants" in data: command += " --grants" if data["grants"] else " --no-grants"
    if "indexes" in data: command += " --indexes" if data["indexes"] else " --no-indexes"
    if "rows" in data: command += " --rows" if data["rows"] else " --no-rows"
    if "constraints" in data: command += " --constraints" if data["constraints"] else " --no-constraints"
    if "triggers" in data: command += " --triggers" if data["triggers"] else " --no-triggers"
    if "direct" in data: command += " --direct" if data["direct"] else " --no-direct"
    if data.get("buffer") is not None: command += f" --buffer {data['buffer']}"
    if data.get("recordlength") is not None: command += f" --recordlength {data['recordlength']}"
    if data.get("inctype"): command += f' --inctype "{data["inctype"]}"'
    if "record" in data: command += " --record" if data["record"] else " --no-record"
    if data.get("statistics"): command += f" --statistics {data['statistics']}"
    if "object_consistent" in data: command += " --object-consistent" if data["object_consistent"] else " --no-object-consistent"
    if data.get("feedback") is not None: command += f" --feedback {data['feedback']}"
    if "resumable" in data: command += " --resumable" if data["resumable"] else " --no-resumable"
    if data.get("resumable_name"): command += f' --resumable-name "{data["resumable_name"]}"'
    if data.get("resumable_timeout") is not None: command += f" --resumable-timeout {data['resumable_timeout']}"
    if "tts_full_check" in data: command += " --tts-full-check" if data["tts_full_check"] else " --no-tts-full-check"
    if data.get("volsize"): command += f' --volsize "{data["volsize"]}"'
    if "transport_tablespace" in data: command += " --transport-tablespace" if data["transport_tablespace"] else " --no-transport-tablespace"
    if data.get("template"): command += f' --template "{data["template"]}"'

    return command

@app.route('/api/preview-export', methods=['POST'])
def api_preview_export():
    data = request.json or {}
    command = build_export_command(data)
    return jsonify({"command": command})

@app.route('/api/export', methods=['POST'])
def api_export():
    data = request.json or {}
    command = build_export_command(data)
    output, code = run_command(command)
    return jsonify({"output": output, "status": "success" if code == 0 else "error"})

@app.route('/api/setup-target', methods=['POST'])
def api_setup():
    command = "python main.py setup-target"
    output, code = run_command(command)
    return jsonify({"output": output, "status": "success" if code == 0 else "error"})

def build_import_command(data):
    command = "python main.py import"

    if data.get("method"):            command += f" --method {data['method']}"
    if data.get("mode"):              command += f" --mode {data['mode']}"
    if data.get("targets"):           command += f' --targets "{data["targets"]}"'
    if data.get("directory"):         command += f' --directory "{data["directory"]}"'
    if data.get("dumpfile"):          command += f' --dumpfile "{data["dumpfile"]}"'
    if data.get("logfile"):           command += f' --logfile "{data["logfile"]}"'
    if data.get("parallel"):          command += f" --parallel {data['parallel']}"
    if data.get("table_exists_action"): command += f" --table-exists-action {data['table_exists_action']}"
    if data.get("content"):           command += f" --content {data['content']}"
    if data.get("exclude"):           command += f' --exclude "{data["exclude"]}"'
    if data.get("include"):           command += f' --include "{data["include"]}"'
    if data.get("query"):             command += f' --query "{data["query"]}"'
    if data.get("remap_schema"):      command += f' --remap-schema "{data["remap_schema"]}"'
    if data.get("remap_tablespace"):  command += f' --remap-tablespace "{data["remap_tablespace"]}"'
    if data.get("remap_datafile"):    command += f' --remap-datafile "{data["remap_datafile"]}"'
    if data.get("remap_data"):        command += f' --remap-data "{data["remap_data"]}"'
    if data.get("remap_table"):       command += f' --remap-table "{data["remap_table"]}"'
    if data.get("network_link"):      command += f' --network-link "{data["network_link"]}"'
    if data.get("flashback_scn"):     command += f' --flashback-scn "{data["flashback_scn"]}"'
    if data.get("flashback_time"):    command += f' --flashback-time "{data["flashback_time"]}"'
    if data.get("version"):           command += f' --version "{data["version"]}"'
    if data.get("job_name"):          command += f' --job-name "{data["job_name"]}"'
    if data.get("sqlfile"):           command += f' --sqlfile "{data["sqlfile"]}"'
    if data.get("transform"):         command += f' --transform "{data["transform"]}"'
    if data.get("transport_tablespaces"): command += f' --transport-tablespaces "{data["transport_tablespaces"]}"'
    if data.get("transport_datafiles"):   command += f' --transport-datafiles "{data["transport_datafiles"]}"'
    if data.get("encryption_password"):   command += f' --encryption-password "{data["encryption_password"]}"'
    if data.get("status") is not None:    command += f" --status {data['status']}"
    if data.get("cluster"):           command += " --cluster"
    if data.get("reuse_datafiles"):   command += " --reuse-datafiles"
    if data.get("skip_unusable_indexes"): command += " --skip-unusable-indexes"
    if data.get("streams_configuration"): command += " --streams-configuration"
    if data.get("transport_full_check"):  command += " --transport-full-check"

    return command

@app.route('/api/preview-import', methods=['POST'])
def api_preview_import():
    data = request.json or {}
    command = build_import_command(data)
    return jsonify({"command": command})

@app.route('/api/import', methods=['POST'])
def api_import():
    data = request.json or {}
    command = build_import_command(data)
    output, code = run_command(command)
    return jsonify({"output": output, "status": "success" if code == 0 else "error"})


@app.route('/api/compare', methods=['POST'])
def api_compare():
    command = "python main.py compare"
    output, code = run_command(command)
    return jsonify({"output": output, "status": "success" if code == 0 else "error"})

if __name__ == '__main__':
    app.run(port=8000, debug=True)
