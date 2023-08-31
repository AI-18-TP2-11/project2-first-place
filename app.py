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
    video_src, region_and_name = get_video_src(cctv_url)
    # template = 'detect.html'
    # if video_src.endswith('m3u8'):
    #     template = 'detectM3u8.html'
    # else:
    #     template = 'detectMp4.html'
    # video_src = r'//cctvsec.ktict.co.kr/9990/0pqKTO1uXKtGWU21VubJ01ErVHVM1kI9JzFmFttstzi/WrzeAwnaNTYed4KnCSSd'
    # video_src = r'http://210.179.218.52:1935/live/171.stream/playlist.m3u8'
    print(video_src)
    # return render_template(template, video_src=video_src, region_and_name='region_and_name')
    # return render_template('detect.html', video_src=video_src, region_and_name='region_and_name')
    return render_template('detect.html', video_src=video_src, region_and_name=region_and_name)

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
    region_and_name = data['region_and_name']
    img_directory = data['img_directory'] # 이미지 저장 경로
    print(data.values())
    return '보내기 성공', 200

if __name__ == '__main__':
    app.run(debug=True)