import pandas as pd
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import os
from tqdm import tqdm
from api import api_key
'''
Flask Map에 cctv 위치 표시 및 링크 연결 계획
도시교통정보센터 개방 데이터에서 제공한 cctv 엑셀 파일을 통해 좌표 정보는 확인 가능하나 링크 정보 수집 필요
일반적으로 개발자 도구를 활용하면 각 cctv 링크에 주소가 표현되나, javascript로 실행되어 Selenium을 통해 백그라운드에서 cctv 링크 클릭 후 주소 정보를 수집하는 방법 사용.
또 cctv 정보가 기재된 엑셀 파일과, 사이트의 cctv id별 지역 정보에 차이가 있어, 확인 후 엑셀 파일 기준으로 merge 작업 수행 
'''
url = f"https://www.utic.go.kr/guide/cctvOpenData.do?key={api_key}"
# 페이지 가져오기
response = requests.get(url)
html = response.content

# BeautifulSoup을 사용하여 HTML 파싱
soup = BeautifulSoup(html, "html.parser")

# <a> 요소 찾기
a_elements = soup.find_all("a", href=lambda href: href and "test" in href)

# 원하는 부분 출력
CCTVID = []
CCTVNAME = []
URL = []
for a_element in a_elements:
    # print(a_element)
    href = a_element["href"]
    CCTVID.append(href.split("('")[1].split("')")[0])
    CCTVNAME.append(a_element.text.split('.')[1])

# 백그라운드에서 실행
chrome_options = Options()
chrome_options.add_argument("--headless")
# chrome_options.add_argument("--disable-gpu")
driver = webdriver.Chrome(options=chrome_options)
driver.get(url)

progress_bar = tqdm(total=len(CCTVID), desc='Processing Documents')

for cctv_id in CCTVID :
    try :
        driver.execute_script(f"return test('{cctv_id}')")
        driver.switch_to.window(driver.window_handles[-1])
        URL.append(driver.current_url)
        driver.close()
        driver.switch_to.window(driver.window_handles[-1])
    except Exception as e:
        print(f"An error occurred for CCTV ID {cctv_id}: {str(e)}")
        URL.append(None)
    progress_bar.update(1)
progress_bar.close()
driver.quit()

# URL 추가된 데이터
data_URL = pd.DataFrame({'CCTVID' : CCTVID, 'CCTVNAME' : CCTVNAME, 'URL' : URL })
# 기존 CCTV 데이터
project_folder_path = os.path.abspath('../..')
data_CCTV = pd.read_excel(os.path.join(project_folder_path,'./CCTV_csv/CCTV.xlsx'), engine='openpyxl')
# CCTVID 기준으로 URL 매핑 
'''.xlsx 파일과 크롤링한 데이터의 CCTVNAME가 다른 경우 존재하여 크롤링 데이터 기준으로 매핑'''
data = data_URL.merge(data_CCTV, on=['CCTVID'])
data = data[['RN','CCTVID','CCTVNAME_x','CENTERNAME','XCOORD','YCOORD','URL']]
data.rename(columns = {'CCTVNAME_x' : 'CCTVNAME'},inplace = True)   
data.to_csv(os.path.join(project_folder_path,'./CCTV_csv/CCTV_URL.csv'),index=False,encoding='euc-kr')
# 데이터 로드 확인
# pd.read_csv('.csv')