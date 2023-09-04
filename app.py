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
    video_src = get_video_src(cctv_url)
    # template = 'detect.html'
    # if video_src.endswith('m3u8'):
    #     template = 'detectM3u8.html'
    # else:
    #     template = 'detectMp4.html'
    # http://www.utic.go.kr/view/map/cctvStream.jsp?cctvid=L902704&cctvname=%25EC%2584%259C%25EC%259A%25B8%2520%25EC%2584%259C%25EC%25B4%2588%2520%25EC%2584%259C%25EC%25B4%2588%25EB%258C%2580%25EB%25A1%259C&kind=EE&cctvip=9990&cctvch=null&id=null&cctvpasswd=null&cctvport=null&minX=127.00182995981353&minY=37.48782667683961&maxX=127.06121163497251&maxY=37.51313060242616
    # video_src = r'//cctvsec.ktict.co.kr/9990/0pqKTO1uXKtGWU21VubJ07na3rnqRars7ib9vSEaDAIK+hrf6T+fs2Nh4irB+FG0'
    # video_src = r'http://210.179.218.52:1935/live/171.stream/playlist.m3u8'
    print(video_src)
    # return render_template(template, video_src=video_src, region_and_name='지역')
    return render_template('detect.html', video_src=video_src, cctv_id=cctv_id, cctv_name=cctv_name, center_name=center_name)
    return render_template('detect.html', video_src=video_src, cctv_id=cctv_id, cctv_name=cctv_name, center_name=center_name)

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
    cctvId = db.Column(db.String)
    cctvName = db.Column(db.String)
    centerName = db.Column(db.String)
    timestamp = db.Column(db.Integer)
    xCenter = db.Column(db.Float)
    yCenter = db.Column(db.Float)
    bWidth = db.Column(db.Float)
    bHeight = db.Column(db.Float)
    iWidth = db.Column(db.Integer)
    iHeight = db.Column(db.Integer)
    score = db.Column(db.Float)
    label = db.Column(db.String)
    imgName = db.Column(db.String)

@app.route('/detect_post', methods=['POST'])
def detect_post():
    '''
    javascript에서 로그 받아오기\n
    현재 dictionary로 구성된 list. dictionary keys == ['cctvId', 'cctvName', 'centerName', 'timestamp', 'xCenter', 'yCenter', 'bWidth', 'bHeight', 'iWidth', 'iHeight', 'score', 'label', 'imgName']
    '''
    data = request.json
    # 데이터 전송
    add_all(data)

    return 'flask 및 db로 전송 성공', 200

@app.route('/upload_generated_dataasdfasdfafsdafsdafsd')
def upload_generated_data():
    '생성한 데이터 업로드'
    import pandas as pd
    df = pd.read_csv('generated_data6.csv')
    add_all_generated(df.values.tolist())
    return '생성 데이터 업로드 성공', 200

def add_all_generated(bulk_data):
    data_to_insert = []
    for datapoint in bulk_data:
        print(datapoint)
        print(len(datapoint))
        data_to_insert.append(
            Submission(
                cctvId = datapoint[0],
                cctvName = datapoint[1],
                centerName = datapoint[2],
                timestamp = datapoint[3],
                xCenter = datapoint[4],
                yCenter = datapoint[5],
                bWidth = datapoint[6],
                bHeight = datapoint[7],
                iWidth = datapoint[8],
                iHeight = datapoint[9],
                score = datapoint[10],
                label = datapoint[11],
                imgName = datapoint[12]
            )
        )

    db.session.add_all(data_to_insert)
    db.session.commit()

def add_all(data):
    # 데이터 전송
    data_to_insert = [Submission(**datapoint) for datapoint in data]

    db.session.add_all(data_to_insert)
    db.session.commit()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)