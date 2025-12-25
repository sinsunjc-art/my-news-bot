import requests
from bs4 import BeautifulSoup
import smtplib
import os
from email.mime.text import MIMEText

# 이메일 정보 (나중에 Settings에서 설정할 값들입니다)
EMAIL_ADDR = os.environ.get('EMAIL_ADDR')
EMAIL_PASS = os.environ.get('EMAIL_PASS')

def get_news():
    results = []
    
    # 1. 산업통상자원부
    try:
        motie_url = "https://www.motie.go.kr/kor/article/ATCL3f469e33d"
        res = requests.get(motie_url, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        post = soup.select_one('.table_basic tbody tr td.left a')
        results.append(f"[산업부] {post.text.strip()}\n링크: https://www.motie.go.kr{post['href']}")
    except:
        results.append("[산업부] 정보를 가져오지 못했습니다.")

    # 2. 방위사업청
    try:
        dapa_url = "https://www.dapa.go.kr/dapa/na/ntt/selectNttList.do?bbsId=443&menuId=356"
        res = requests.get(dapa_url, verify=False, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        post = soup.select_one('table.board_list tbody tr td.al_l a')
        results.append(f"[방사청] {post.text.strip()}\n링크: https://www.dapa.go.kr{post['href']}")
    except:
        results.append("[방사청] 정보를 가져오지 못했습니다.")
        
    return "\n\n".join(results)

def run():
    content = get_news()
    
    # 이전 내용과 비교 (중복 방지용 간단 로직)
    last_content = ""
    if os.path.exists("last_title.txt"):
        with open("last_title.txt", "r", encoding="utf-8") as f:
            last_content = f.read().strip()

    if content != last_content:
        # 메일 보내기
        msg = MIMEText(content)
        msg['Subject'] = "🔔 데일리 보도자료 업데이트"
        msg['From'] = EMAIL_ADDR
        msg['To'] = EMAIL_ADDR # 본인에게 발송

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(EMAIL_ADDR, EMAIL_PASS)
            server.send_message(msg)
        
        # 새로운 내용 저장
        with open("last_title.txt", "w", encoding="utf-8") as f:
            f.write(content)
        print("새로운 공지가 있어 메일을 보냈습니다.")
    else:
        print("새로운 공지가 없습니다.")

if __name__ == "__main__":
