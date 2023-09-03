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
    video_src = r'//cctvsec.ktict.co.kr/9990/0pqKTO1uXKtGWU21VubJ0xfQj4uNr+OzfMzpev7ZSjqBhMpfdnThPiGF9jLzPhXS'
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
    # cctv_id, cctv_name, center_name, timestamp, x, y, bwidth, bheight, width, height, score, label, img_name
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
    img_name = db.Column(db.String)

@app.route('/detect_post', methods=['POST'])
def detect_post():
    '''
    javascript에서 로그 받아오기\n
    현재 data.keys() == ['bboxes', 'scores', 'labels', 'timestamp', 'width', 'height', region_and_name', 'img_name', 'filterCheck]
    '''
    data = request.json
    bboxes = data['bboxes'] # nested array: [[x, y, w, h],...]
    scores = data['scores'] # [0.6, 0.89,...]
    labels = data['labels'] # [0, 4,...] # yolo 라벨 0-23
    timestamp = data['timestamp'] # unix
    width = data['width'] # 이미지 width
    height = data['height'] # 이미지 height
    cctv_id = data['cctvId'] # cctv id
    cctv_name = data['cctvName'] # cctv name
    center_name = data['centerName'] # center name
    img_name = data['imgName'] # 이미지 저장 경로
    filter_check = data['filterCheck'] # 위반사항 확인 list: 1이면 위반, 0이면 정상

    print(data.values())

    # db로 데이터 전송
    zipped = zip(bboxes, scores, labels)
    add_all(cctv_id, cctv_name, center_name, timestamp, zipped, width, height, img_name, filter_check)

    return 'flask 및 db로 전송 성공', 200

@app.route('/upload_generated_dataasdfasdfafsdafsdafsd')
def upload_generated_data():
    '생성한 데이터 업로드'
    import pandas as pd
    df = pd.read_csv('generated_data5.csv')
    add_all_generated(df.values.tolist())
    return '생성 데이터 업로드 성공', 200

def add_all_generated(bulk_data):
    data_to_insert = []
    for datapoint in bulk_data:
        print(datapoint)
        print(len(datapoint))
        data_to_insert.append(
            Submission(
                cctv_id = datapoint[0],
                cctv_name = datapoint[1],
                center_name = datapoint[2],
                timestamp = datapoint[3],
                x = datapoint[4],
                y = datapoint[5],
                bwidth = datapoint[6],
                bheight = datapoint[7],
                width = datapoint[8],
                height = datapoint[9],
                score = datapoint[10],
                label = datapoint[11],
                img_name = datapoint[12]
            )
        )

    db.session.add_all(data_to_insert)
    db.session.commit()

def add_all(cctv_id, cctv_name, center_name, timestamp, zipped, width, height, img_name, filter_check):
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
            img_name = img_name if filter_check[idx] else None
        )
        for idx, (bbox, score, label) in enumerate(zipped)
    ]

    db.session.add_all(data_to_insert)
    db.session.commit()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)