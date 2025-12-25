import requests
from bs4 import BeautifulSoup
import smtplib
import os
import urllib3
from email.mime.text import MIMEText

# 경고 메시지 무시 (보안 인증서 관련)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

EMAIL_ADDR = os.environ.get('EMAIL_ADDR')
EMAIL_PASS = os.environ.get('EMAIL_PASS')

# 실제 브라우저처럼 보이기 위한 더 상세한 설정
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
}

def fetch_content(url, verify=True):
    """사이트 접속 시도 함수"""
    try:
        res = requests.get(url, headers=HEADERS, verify=verify, timeout=20)
        res.raise_for_status()
        return res.text
    except Exception as e:
        return None

def get_news():
    results = []
    
    # 1. 산업통상자원부
    html = fetch_content("https://www.motie.go.kr/kor/article/ATCL3f469e33d")
    if html:
        soup = BeautifulSoup(html, 'html.parser')
        post = soup.select_one('td.left a')
        if post:
            results.append(f"[산업부] {post.text.strip()}\n링크: https://www.motie.go.kr{post['href']}")
    
    # 2. 방위사업청 (인증서 검증 제외)
    html = fetch_content("https://www.dapa.go.kr/dapa/na/ntt/selectNttList.do?bbsId=443&menuId=356", verify=False)
    if html:
        soup = BeautifulSoup(html, 'html.parser')
        post = soup.select_one('td.al_l a')
        if post:
            results.append(f"[방사청] {post.text.strip()}\n링크: https://www.dapa.go.kr{post['href']}")

    # 3. 국방부
    html = fetch_content("https://www.mnd.go.kr/mbshome/mnd/mnd_1/mnd_1_1/index.jsp")
    if html:
        soup = BeautifulSoup(html, 'html.parser')
        post = soup.select_one('td.title a')
        if post:
            link = post['href']
            if not link.startswith('http'): link = "https://www.mnd.go.kr" + link
            results.append(f"[국방부] {post.text.strip()}\n링크: {link}")

    # 하나도 가져오지 못했을 경우 예외 처리
    if not results:
        return "모든 사이트의 접속이 일시적으로 차단되었습니다. 나중에 다시 시도합니다."
        
    return "\n\n".join(results)

def run():
    content = get_news()
    
    last_content = ""
    if os.path.exists("last_title.txt"):
        with open("last_title.txt", "r", encoding="utf-8") as f:
            last_content = f.read().strip()

    if content != last_content and "차단되었습니다" not in content:
        msg = MIMEText(content)
        msg['Subject'] = "🔔 데일리 보도자료 업데이트 (국방/산업/방사)"
        msg['From'] = EMAIL_ADDR
        msg['To'] = EMAIL_ADDR

        try:
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(EMAIL_ADDR, EMAIL_PASS)
                server.send_message(msg)
            
            with open("last_title.txt", "w", encoding="utf-8") as f:
                f.write(content)
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    run()
