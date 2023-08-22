from flask import Flask, render_template
import requests

app = Flask(__name__)

# API 키
# API_KEY = "XxTwsc3p80QmOWMFWzJ3Y6W4zJmhHXjxKGxpDAeQS9fxU8tEPej1yQhboGwXhk"
API_KEY = f"XxTwsc3p80QmOWMFWzJ3Y6W4zJmhHXjxKGxpDAeQS9fxU8tEPej1yQhboGwXhk&cctvid=L280042&cctvName=%25EC%2598%25A5%25ED%258F%25AC%25EB%258F%2599%2520%25EC%2598%25A5%25ED%258F%25AC%25EC%2582%25BC%25EA%25B1%25B0%25EB%25A6%25AC&kind=t&cctvip=null&cctvch=9&id=637bef0325205&cctvpasswd=null&cctvport=null"

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
    
# @app.route('/')
# def index():
#     # API를 사용하여 CCTV 영상 URL 가져오기
#     api_url = f"https://www.utic.go.kr/view/map/openDataCctvStream.jsp?key={API_KEY}"
#     response = requests.get(api_url)
#     cctv_url = response.text

#     # CCTV 영상 URL을 웹 페이지에 임베드하여 표시
#     return render_template('index.html', cctv_url=cctv_url)

# if __name__ == '__main__':
#     app.run(debug=True)