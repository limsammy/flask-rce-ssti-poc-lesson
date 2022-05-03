from flask import Flask, render_template, render_template_string, request

app = Flask(__name__)


@app.route("/", methods=["GET"])
def index():
    name = request.args.get("name") or None
    if name:
        template = (
            """<p> Hello, %s 
        """
            % name
        )

    else:
        template = """
        <p> What yor name? </p>
        <form method="get" action="/">
        <p>
            Enter your name:
            <input type="text" name="name">
        </p>
        <input type="submit" value="Submit">
        </form>"""

    return render_template_string(template, name=name)

    # name = request.args.get("name") or None  # get untrusted query param
    # return render_template("index.html", name=name)  # render it into template
