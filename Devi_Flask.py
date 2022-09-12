from flask import Flask
app=Flask(__name__)
@app.route("/")
def first_prog():
    return "<p>First program</p>"
