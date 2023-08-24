'''
ffmpeg 프로그램 및 라이브러리 설치 필요
https://ffmpeg.org/download.html#build-windows에서 프로그램 설치 및 환경변수 추가 
bash : ffmpeg -version을 통해 설치 확인 가능
 '''
# ffmpeg-python 라이브러리 설치
# !pip install ffmpeg-python
import subprocess
import time
import datetime

# 파일명에 날짜정보 추가를 위한 변수 설정
current_datetime = datetime.datetime.now()
year = current_datetime.strftime("%Y")
month = current_datetime.strftime("%m")
day = current_datetime.strftime("%d")
hour = current_datetime.strftime("%H")
minute = current_datetime.strftime("%M")
second = current_datetime.strftime("%S")

# 지역 이름 설정 / ex. 역삼역
region_name = '전주_병무청오거리'
# 실시간 영상 데이터(.m3u8) url 입력
stream_url = "http://115.92.162.198:1935/live/CCTV_21.stream/playlist.m3u8"

# 저장할 동영상 파일명 설정 / ex. 역삼역_20230824_172230.mp4
output_filename = f"{region_name}_{year}{month}{day}_{hour}{minute}{second}.mp4"

# 녹화할 시간 (초 단위)
recording_duration = 1220  # 약 20분 동안 녹화 // 20초는 영상 변환 딜레이로 발생할 수 있는 에러 방지를 위해 여유 시간 추가

# 시작 시간
start_time = time.time()

# ffmpeg 명령어 실행
command = [
    "ffmpeg",
    "-i", stream_url,
    "-c:v", "copy",
    "-c:a", "aac",
    "-strict", "experimental",
    "-bsf:a", "aac_adtstoasc",  # AAC 오디오의 포맷 변환
    "-t", "1200", # 영상 시간 설정 // ex. 20분
    output_filename
]

# 녹화 시작
subprocess.Popen(command)

# 지정한 녹화 시간 동안 대기하며 녹화를 진행
while time.time() - start_time < recording_duration:
    time.sleep(1)  # 1초마다 체크

# 녹화 중지
subprocess.call(["taskkill", "/F", "/IM", "ffmpeg.exe"])  # Windows 용
# subprocess.call(["pkill", "-f", "ffmpeg"])  # macOS 용
# subprocess.call(["pkill", "ffmpeg"])  # Linux 용

print("녹화가 완료되었습니다.")