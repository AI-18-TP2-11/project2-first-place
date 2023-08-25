from flask import Flask, render_template
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/main')
def main():
    return render_template('main.html')

@app.route('/detect')
def detect():
    return render_template('detect.html')

@app.route('/select')
def select():
    return render_template('select.html')

if __name__ == '__main__':
    app.run(debug=True)