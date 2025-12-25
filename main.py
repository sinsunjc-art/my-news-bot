import requests
from bs4 import BeautifulSoup
import smtplib
import os
from email.mime.text import MIMEText

# 환경변수 설정
EMAIL_ADDR = os.environ.get('EMAIL_ADDR')
EMAIL_PASS = os.environ.get('EMAIL_PASS')

# 로봇 차단을 방지하기 위한 브라우저 설정
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def get_news():
    results = []
    
    # 1. 산업통상자원부
    try:
        url = "https://www.motie.go.kr/kor/article/ATCL3f469e33d"
        res = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(res.text, 'html.parser')
        # 목록의 첫 번째 게시물 제목 찾기
        post = soup.select_one('td.left a')
        if post:
            title = post.text.strip()
            link = "https://www.motie.go.kr" + post['href']
            results.append(f"[산업부] {title}\n링크: {link}")
        else:
            results.append("[산업부] 게시글을 찾지 못했습니다.")
    except Exception as e:
        results.append(f"[산업부] 연결 오류: {e}")

    # 2. 방위사업청
    try:
        url = "https://www.dapa.go.kr/dapa/na/ntt/selectNttList.do?bbsId=443&menuId=356"
        # 방사청은 보안 인증서 무시(verify=False)가 필요할 때가 많음
        res = requests.get(url, headers=HEADERS, verify=False, timeout=15)
        soup = BeautifulSoup(res.text, 'html.parser')
        post = soup.select_one('table.board_list tbody tr td.al_l a')
        if post:
            title = post.text.strip()
            link = "https://www.dapa.go.kr" + post['href']
            results.append(f"[방사청] {title}\n링크: {link}")
        else:
            results.append("[방사청] 게시글을 찾지 못했습니다.")
    except Exception as e:
        results.append(f"[방사청] 연결 오류: {e}")

    # 3. 국방부
    try:
        url = "https://www.mnd.go.kr/mbshome/mnd/mnd_1/mnd_1_1/index.jsp"
        res = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(res.text, 'html.parser')
        post = soup.select_one('td.title a')
        if post:
            title = post.text.strip()
            link = post['href']
            if not link.startswith('http'):
                link = "https://www.mnd.go.kr" + link
            results.append(f"[국방부] {title}\n링크: {link}")
        else:
            results.append("[국방부] 게시글을 찾지 못했습니다.")
    except Exception as e:
        results.append(f"[국방부] 연결 오류: {e}")
        
    return "\n\n".join(results)

def run():
    content = get_news()
    
    # 이전 내용 불러오기
    last_content = ""
    if os.path.exists("last_title.txt"):
        with open("last_title.txt", "r", encoding="utf-8") as f:
            last_content = f.read().strip()

    # 내용 변화가 있을 때만 메일 발송
    if content != last_content:
        msg = MIMEText(content)
        msg['Subject'] = "🔔 데일리 보도자료 업데이트 (국방/산업/방사)"
        msg['From'] = EMAIL_ADDR
        msg['To'] = EMAIL_ADDR

        try:
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(EMAIL_ADDR, EMAIL_PASS)
                server.send_message(msg)
            
            # 새로운 내용을 저장하여 다음번 중복 방지
            with open("last_title.txt", "w", encoding="utf-8") as f:
                f.write(content)
            print("성공적으로 메일을 보냈습니다!")
        except Exception as e:
            print(f"메일 발송 실패: {e}")
    else:
        print("새로운 공지가 없어 메일을 보내지 않았습니다.")

if __name__ == "__main__":
    run()
