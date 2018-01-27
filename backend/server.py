from flask import Flask
import json
app = Flask(__name__)

@app.route('/')
def hello_world():
    return json.dumps({'test':'test'})