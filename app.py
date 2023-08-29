from flask import Flask, render_template, request, send_file
import os
import csv
from get_video_src import get_video_src

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/main')
def main():
    return render_template('main.html')

@app.route('/detect')
def detect():
    cctv_url = request.args.get('url')
    video_src = get_video_src(cctv_url)
    return render_template('detect.html', video_src=video_src)

def parse_csv():
    data = []
    with open('static/CCTV.csv', 'r', encoding='utf-8') as csvfile:
        csvreader = csv.DictReader(csvfile)
        for row in csvreader:
            data.append(row)
    return data

@app.route('/select')
def select():
    csv_data = parse_csv()
    return render_template('select.html', csv_data=csv_data)

if __name__ == '__main__':
    app.run(debug=True)