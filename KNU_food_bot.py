import bs4
import requests
import schedule
import time
from datetime import datetime

# Slack 정보
my_Token = "xoxb-1999813266115-3164773968226-rsxkb9zMI6wvSnARovBdYV6X"
my_channel = '#knu'

def post_message(token, channel, text):
    # attachments = json.dumps(attachments)
    response = requests.post("https://slack.com/api/chat.postMessage",
        headers={"Authorization": "Bearer "+token},
        data={"channel": channel,"text": text}
    )

# 요일 구분 딕셔너리 생성
weekdays_dict = {
    0 : '월',
    1 : '화', 
    2 : '수', 
    3 : '목', 
    4 : '금', 
    5 : '토', 
    6 : '일'
}

# time 설정
today = datetime.today()
today_date = today.strftime('%m월 %d일') # YYYY-MM-DD 형식으로 날짜표시
weekdays = datetime.weekday(today) # 오늘이 무슨요일인지 0 ~ 6 의 숫자로 표현
now_time = today.strftime('%X')
    
# 식사 시간 딕셔너리 생성
meal_time = {
    0 : '<아침> 08:00 ~ 09:00',
    1 : '<점심> 11:30/12:00(휴일) ~ 13:00',
    2 : '<저녁> 17:30 ~ 18:30'
}

# 메뉴 크롤링
month = "03"
url = "https://dorm.knu.ac.kr/scdorm/_new_ver/newlife/05.php?type=diary_form&mode=diary&year=2022&month=" + month + "&get_mode=2"
raw = requests.get(url)

html = bs4.BeautifulSoup(raw.content.decode('euc-kr', 'replace'), 'html.parser')

target = html.find('div',{'class':'menu_left'})

menu = target.find_all('p')

# 오늘의 메뉴 -> list에 저장
today_food = []

for food in menu:
    today_food.append(food.text)

# 식사 시간 출력물 생성
moring = meal_time[0] + today_food[0]
lunch = meal_time[1] + today_food[1]
dinner = meal_time[2] + today_food[2]

title = "[" + today_date + " " + weekdays_dict[weekdays] + "요일" + " 도미토랑 식단표]"

# 출력
print(title)
print(moring)
print()
print(lunch)
print()
print(dinner)

# Slack 전송
def slack_run_time():
    post_message(my_Token, my_channel, title)
    post_message(my_Token, my_channel, meal_time[0])
    post_message(my_Token, my_channel, today_food[0])
    post_message(my_Token, my_channel, meal_time[1])
    post_message(my_Token, my_channel, today_food[1])
    post_message(my_Token, my_channel, meal_time[2])
    post_message(my_Token, my_channel, today_food[2])

#매일 00:05마다 동작 
schedule.every().day.at("00:05").do(slack_run_time) 
    
#무한 루프
while True: 
    schedule.run_pending() 
    time.sleep(1)
