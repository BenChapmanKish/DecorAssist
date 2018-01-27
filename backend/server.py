from flask import Flask
from flask import request
import json

app = Flask(__name__)

@app.route('/', methods=['GET','POST'])
def main():
    data = request.data
    print(data)
    if request.method == 'POST':
        print()
        return json.dumps({'success':True})
    elif request.method == 'GET':
        return json.dumps({'test':'test'})