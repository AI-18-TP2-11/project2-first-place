from flask import Flask, render_template, request, send_file
import os
import csv
from get_video_src import get_video_src
from flask_sqlalchemy import SQLAlchemy
import json


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///submission.db'  # SQLite 데이터베이스를 사용합니다.
db = SQLAlchemy(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/main')
def main():
    return render_template('main.html')

@app.route('/detect')
def detect():
    cctv_url = request.args.get('url')
    cctv_id = request.args.get('cctvId')
    cctv_name = request.args.get('cctvName')
    center_name = request.args.get('centerName')
    region_and_name = cctv_name
    # video_src, region_and_name = get_video_src(cctv_url)
    # template = 'detect.html'
    # if video_src.endswith('m3u8'):
    #     template = 'detectM3u8.html'
    # else:
    #     template = 'detectMp4.html'
    video_src = r'//cctvsec.ktict.co.kr/9990/0pqKTO1uXKtGWU21VubJ055VkqvK2hm+T3A/l5Oyigsd6J7dr2Z2rf9zB1m4cli8'
    # video_src = r'http://210.179.218.52:1935/live/171.stream/playlist.m3u8'
    print(video_src)
    # return render_template(template, video_src=video_src, region_and_name='지역')
    return render_template('detect.html', video_src=video_src, region_and_name='지역', cctv_id=cctv_id, cctv_name=cctv_name, center_name=center_name)
    return render_template('detect.html', video_src=video_src, region_and_name=region_and_name, cctv_id=cctv_id, cctv_name=cctv_name, center_name=center_name)

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

# DB 생성 형식
class Submission(db.Model):
    # cctv_id, cctv_name, center_name, timestamp, x1, x2, y1, y2, width, height, score, label, img_directory
    id = db.Column(db.Integer, primary_key=True)
    cctv_id = db.Column(db.String)
    cctv_name = db.Column(db.String)
    center_name = db.Column(db.String)
    timestamp = db.Column(db.Integer)
    x = db.Column(db.Float)
    y = db.Column(db.Float)
    bwidth = db.Column(db.Float)
    bheight = db.Column(db.Float)
    width = db.Column(db.Integer)
    height = db.Column(db.Integer)
    score = db.Column(db.Float)
    label = db.Column(db.String)
    img_directory = db.Column(db.String)

@app.route('/test', methods=['POST'])
def test_post():
    '''
    javascript에서 로그 받아오기\n
    현재 data.keys() == ['bboxes', 'scores', 'labels', 'timestamp', 'width', 'height', region_and_name', 'img_directory']
    '''
    data = request.json
    bboxes = data['bboxes'] # nested array: [[x, y, w, h],...]
    scores = data['scores'] # [0.6, 0.89,...]
    labels = data['labels'] # [0, 4,...] # yolo 라벨 0-23
    timestamp = data['timestamp'] # unix
    width = data['width'] # 이미지 width
    height = data['height'] # 이미지 height
    cctv_id = data['cctv_id'] # cctv id
    cctv_name = data['cctv_name'] # cctv name
    center_name = data['center_name'] # center name
    img_directory = data['img_directory'] # 이미지 저장 경로

    print(data.values())

    # 보낼 데이터
    zipped = zip(bboxes, scores, labels)
    data_to_insert = [
        Submission(
            cctv_id = cctv_id,
            cctv_name = cctv_name,
            center_name = center_name,
            timestamp = timestamp,
            x = bbox[0],
            y = bbox[1],
            bwidth = bbox[2],
            bheight = bbox[3],
            width = width,
            height = height,
            score = score,
            label = label,
            img_directory = img_directory
        )
        for bbox, score, label in zipped
    ]

    db.session.add_all(data_to_insert)
    db.session.commit()    

    return 'flask 및 db로 전송 성공', 200

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)