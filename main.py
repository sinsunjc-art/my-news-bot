import requests
from bs4 import BeautifulSoup
import smtplib
import os
from email.mime.text import MIMEText

# 환경변수 읽기
EMAIL_ADDR = os.environ.get('EMAIL_ADDR')
EMAIL_PASS = os.environ.get('EMAIL_PASS')

def get_news():
    results = []
    
    # 1. 산업통상자원부
    try:
        motie_url = "https://www.motie.go.kr/kor/article/ATCL3f469e33d"
        res = requests.get(motie_url, timeout=15)
        soup = BeautifulSoup(res.text, 'html.parser')
        post = soup.select_one('.table_basic tbody tr td.left a')
        results.append(f"[산업부] {post.text.strip()}\n링크: https://www.motie.go.kr{post['href']}")
    except Exception as e:
        results.append(f"[산업부] 정보를 가져오지 못했습니다. ({e})")

    # 2. 방위사업청
    try:
        dapa_url = "https://www.dapa.go.kr/dapa/na/ntt/selectNttList.do?bbsId=443&menuId=356"
        res = requests.get(dapa_url, verify=False, timeout=15)
        soup = BeautifulSoup(res.text, 'html.parser')
        post = soup.select_one('table.board_list tbody tr td.al_l a')
        results.append(f"[방사청] {post.text.strip()}\n링크: https://www.dapa.go.kr{post['href']}")
    except Exception as e:
        results.append(f"[방사청] 정보를 가져오지 못했습니다. ({e})")

    # 3. 국방부 (추가됨)
    try:
        mnd_url = "https://www.mnd.go.kr/mbshome/mnd/mnd_1/mnd_1_1/index.jsp"
        res = requests.get(mnd_url, timeout=15)
        soup = BeautifulSoup(res.text, 'html.parser')
        # 국방부 보도자료 첫 번째 게시물 추출
        post = soup.select_one('table.board_list tbody tr td.title a')
        results.append(f"[국방부] {post.text.strip()}\n링크: https://www.mnd.go.kr{post['href']}")
    except Exception as e:
        results.append(f"[국방부] 정보를 가져오지 못했습니다. ({e})")
        
    return "\n\n".join(results)

def run():
    content = get_news()
    
    # 중복 체크 로직 (이전 내용과 비교)
    last_content = ""
    if os.path.exists("last_title.txt"):
        with open("last_title.txt", "r", encoding="utf-8") as f:
            last_content = f.read().strip()

    if content != last_content:
        # 이메일 구성
        msg = MIMEText(content)
        msg['Subject'] = "🔔 데일리 보도자료 업데이트 (국방/산업/방사)"
        msg['From'] = EMAIL_ADDR
        msg['To'] = EMAIL_ADDR

        # 메일 발송 서버 연결
        try:
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(EMAIL_ADDR, EMAIL_PASS)
                server.send_message(msg)
            
            # 최신 내용 저장
            with open("last_title.txt", "w", encoding="utf-8") as f:
                f.write(content)
            print("새 글 발견! 메일 발송 성공.")
        except Exception as e:
            print(f"메일 발송 중 오류 발생: {e}")
    else:
        print("새로운 업데이트가 없습니다.")

if __name__ == "__main__":
    run()
