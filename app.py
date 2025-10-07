from flask import Flask, request, send_file, jsonify, send_from_directory
from datetime import datetime, timedelta
import os.path
import json
import os
import uuid
import brotli

with open("./main.html", "rb") as f:
    file = f.read()

min_html = brotli.compress(file, quality=11)

def get_time():
    time_obj = datetime.utcnow() + timedelta(hours=8)
    return time_obj.strftime("%Y.%m.%d %H:%M")


app = Flask(__name__)


UPLOAD_FOLDER = "./data/files"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 1024 * 1024 * 1024


@app.route("/", methods=["GET"])
def handle_index():
    return min_html, 200, {"Content-Encoding":"br", "Content-Type":"text/html; charset=utf-8", "Strict-Transport-Security":"max-age=31536000; includeSubDomains", "Content-Security-Policy": "default-src 'none'; script-src 'unsafe-inline' 'self'; manifest-src 'self'; style-src 'nonce-ILOVECYJ'; connect-src 'self' blob:; img-src data: blob:"}

@app.route("/service_worker.js", methods=["GET"])
def handle_sw():
    return send_file("./service_worker.js")

@app.route("/app.webmanifest", methods=["GET"])
def handle_manifest():
    return send_file("./app.webmanifest")

@app.route("/old", methods=["GET"])
def handle_old():
    return send_file("./main_old.html")

@app.route("/join", methods=["POST"])
def handle_join():
    room = request.json.get("room").strip()
    filename = f"./data/{room}.json"
    if not os.path.isfile(filename):
        new_file = open(filename, "w")
        new_file.write("[]")
        new_file.close()
    return send_file(filename)

@app.route("/file", methods=["POST"])
def handle_file():
    file = request.files.get("file")
    room = request.form.get('room', '').strip()
    if file and file.filename:
        ext = os.path.splitext(file.filename)[1]
        unique_filename = str(uuid.uuid4()) + ext
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], unique_filename)
        file.save(file_path)
        msg = f"FILE:{unique_filename}"
        with open(f"./data/{room}.json", "r+") as f:
            msgs = json.load(f)
            f.seek(0)
            msgs.insert(0, [msg, get_time()])
            json.dump(msgs, f)
    return jsonify("complete")

@app.route("/msg", methods=["POST"])
def handle_msg():
    data = request.json
    room = data.get("room").strip()
    msg = data.get("msg").strip()
    with open(f"./data/{room}.json", "r+") as f:
        msgs = json.load(f)
        f.seek(0)
        msgs.insert(0, [msg, get_time()])
        json.dump(msgs, f)
    return jsonify("complete")


@app.route("/data", methods=["POST"])
def handle_data():
    filename = request.json.get("filename")
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


