import requests
from bs4 import BeautifulSoup
import smtplib
import os
from email.mime.text import MIMEText

# 환경변수 설정
EMAIL_ADDR = os.environ.get('EMAIL_ADDR')
EMAIL_PASS = os.environ.get('EMAIL_PASS')

def get_news():
    results = []
    
    # 1. 산업통상자원부 (구조 보강)
    try:
        url = "https://www.motie.go.kr/kor/article/ATCL3f469e33d"
        res = requests.get(url, timeout=15)
        soup = BeautifulSoup(res.text, 'html.parser')
        # 게시판 첫번째 행의 제목 부분을 더 명확히 타겟팅
        post = soup.select_one('.table_basic tbody tr td.left a')
        if post:
            results.append(f"[산업부] {post.text.strip()}\n링크: https://www.motie.go.kr{post['href']}")
        else:
            results.append("[산업부] 새 게시글 구조를 찾을 수 없습니다.")
    except Exception as e:
        results.append(f"[산업부] 연결 오류: {e}")

    # 2. 방위사업청 (구조 보강)
    try:
        url = "https://www.dapa.go.kr/dapa/na/ntt/selectNttList.do?bbsId=443&menuId=356"
        res = requests.get(url, verify=False, timeout=15)
        soup = BeautifulSoup(res.text, 'html.parser')
        post = soup.select_one('td.al_l a')
        if post:
            results.append(f"[방사청] {post.text.strip()}\n링크: https://www.dapa.go.kr{post['href']}")
        else:
            results.append("[방사청] 새 게시글 구조를 찾을 수 없습니다.")
    except Exception as e:
        results.append(f"[방사청] 연결 오류: {e}")

    # 3. 국방부 (구조 보강)
    try:
        url = "https://www.mnd.go.kr/mbshome/mnd/mnd_1/mnd_1_1/index.jsp"
        res = requests.get(url, timeout=15)
        soup = BeautifulSoup(res.text, 'html.parser')
        # 국방부 게시판의 제목 클래스 타겟팅
        post = soup.select_one('td.title a')
        if post:
            # 국방부 링크는 상대경로인 경우가 많아 처리
            link = post['href']
            if not link.startswith('http'):
                link = "https://www.mnd.go.kr" + link
            results.append(f"[국방부] {post.text.strip()}\n링크: {link}")
        else:
            results.append("[국방부] 새 게시글 구조를 찾을 수 없습니다.")
    except Exception as e:
        results.append(f"[국방부] 연결 오류: {e}")
        
    return "\n\n".join(results)

def run():
    content = get_news()
    
    last_content = ""
    if os.path.exists("last_title.txt"):
        with open("last_title.txt", "r", encoding="utf-8") as f:
            last_content = f.read().strip()

    # 내용이 달라졌을 때만 발송
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
            
            with open("last_title.txt", "w", encoding="utf-8") as f:
                f.write(content)
            print("발송 완료!")
        except Exception as e:
            print(f"메일 발송 실패: {e}")
    else:
        print("업데이트 없음")

if __name__ == "__main__":
    run()
