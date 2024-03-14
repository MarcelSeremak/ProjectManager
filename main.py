from flask import Flask, request, render_template, redirect, url_for


app = Flask(__name__)


@app.route("/")
def starting_page():
    return render_template("homepage.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")

if __name__ == "__main__":
    app.run(debug=True)