from flask import Flask, render_template, render_template_string, request

app = Flask(__name__)


@app.route("/", methods=["GET"])
def index():
    name = request.args.get("name") or None  # get untrusted query param
    return render_template("index.html", name=name)  # render it into template
