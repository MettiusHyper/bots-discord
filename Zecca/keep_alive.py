from flask import Flask, send_file, render_template, request
from threading import Thread
import os

app = Flask("")

@app.route("/")
def main():
    return render_template("index.html")

@app.route("/regolamento")
def regolamento():
    return render_template("regolamento.html")

@app.route("/hosting")
def hosting():
    return render_template("hosting.html")

@app.route('/downloads', methods = ["POST", "GET"])
def downloads():
    return render_template("downloads.html", textures = os.listdir("./textures"))

@app.route('/download', methods = ["POST", "GET"])
def downloadFile():
    print(request.form['requested_texture'])
    try:
        path = request.form['requested_texture']
    except:
        path = sorted(os.listdir('./textures'))[0]
    path = f"textures/{path}"
    return send_file(path, as_attachment=True)

def run():
    app.run(host = "0.0.0.0", port = 8080)

def host():
    server = Thread(target = run)
    server.start()
