'''
cctv url에서 video src 추출하는 모듈\n
페이지 렌더링 해야지 src 제대로 작성됨. 현재 selenium headless 모드 사용중.
'''
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def get_video_url(iframe_url=r'http://www.utic.go.kr/view/map/cctvStream.jsp?cctvid=L902704&cctvname=%25EC%2584%259C%25EC%259A%25B8%2520%25EC%2584%259C%25EC%25B4%2588%2520%25EC%2584%259C%25EC%25B4%2588%25EB%258C%2580%25EB%25A1%259C&kind=EE&cctvip=9990&cctvch=null&id=null&cctvpasswd=null&cctvport=null&minX=127.00182995981353&minY=37.48782667683961&maxX=127.06121163497251&maxY=37.51313060242616'):
    'iframe_url로부터 video 태그의 src url 추출해서 반환'
    options = Options()
    options.add_argument('--headless') # 백그라운드에서 재생

    driver = Chrome(options)
    driver.get(iframe_url)

    # 로딩 기다리는 최대 시간 10초
    wait = WebDriverWait(driver, 10)

    video = wait.until(EC.presence_of_element_located((By.TAG_NAME, 'source')))
    src = video.get_attribute('src')
    print(f'video src: {src}')

    return src

if __name__ == '__main__':
    get_video_url()