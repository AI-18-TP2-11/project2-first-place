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
import concurrent.futures

'''
파일 변환 완료 후 프로그램 강제 종료  Ctrl + C
'''

def record_video(region_name, stream_url, recording_duration):

    # 파일명에 날짜정보 추가를 위한 변수 설정
    current_datetime = datetime.datetime.now()
    year = current_datetime.strftime("%Y")
    month = current_datetime.strftime("%m")
    day = current_datetime.strftime("%d")
    hour = current_datetime.strftime("%H")
    minute = current_datetime.strftime("%M")
    second = current_datetime.strftime("%S")



    # 저장할 동영상 파일명 설정 / ex. 역삼역_20230824_172230.mp4
    output_filename = f"{region_name}_{year}{month}{day}_{hour}{minute}{second}.mp4"
    # ffmpeg 명령어 실행
    command = [
        "ffmpeg",
        "-i", stream_url,
        "-c:v", "copy",
        "-c:a", "aac",
        "-strict", "experimental",
        "-bsf:a", "aac_adtstoasc",  # AAC 오디오의 포맷 변환
        "-t", str(recording_duration), # 영상 시간 설정 // ex. 20분
        output_filename
    ]

    subprocess.Popen(command)
    print(f"{output_filename} 녹화가 완료되었습니다.")

def record_videos_in_parallel():
   region_streams = [
      {"region_name": "부산_해운대바다", "stream_url": "http://61.43.246.225:1935/rtplive/cctv_86.stream/playlist.m3u8", "recording_duration": 1220},
      {"region_name": "부산_해운대이름난암소갈비", "stream_url": "http://61.43.246.226:1935/rtplive/cctv_406.stream/playlist.m3u8", "recording_duration": 1220},
      {"region_name": "부산_동래롯데", "stream_url": "http://61.43.246.225:1935/rtplive/cctv_19.stream/playlist.m3u8", "recording_duration": 1220},

   ]
   with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(record_video, **stream_info) for stream_info in region_streams]
        for future in concurrent.futures.as_completed(futures):
            pass

record_videos_in_parallel()

