import time
import pyupbit
import datetime
import requests

# 업비트 api & Slack 토큰값 불러오기
# f = open("E:/Python_Project/Auto coin/My_api.txt", "r")
# lines = f.readlines()
# f.close()

# 업비트 api 정보
access = "abcd"
secret = "abcd"

# Slack 정보
myToken = "abcd"
channel_name = "#coin"

# coin 정보
coin = "ETH"
best_k = 0.1

def post_message(token, channel, text):
    """슬랙 메시지 전송"""
    response = requests.post("https://slack.com/api/chat.postMessage",
        headers={"Authorization": "Bearer "+token},
        data={"channel": channel,"text": text}
    )

def get_target_price(ticker, k):
    """변동성 돌파 전략으로 매수 목표가 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count = 2)
    target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * k
    return target_price

def get_start_time(ticker):
    """시작 시간 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
    start_time = df.index[0]
    return start_time

def get_ma15(ticker):
    """15일 이동 평균선 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=15)
    ma15 = df['close'].rolling(15).mean().iloc[-1]
    return ma15

def get_balance(ticker):
    """잔고 조회"""
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0
    return 0

def get_current_price(ticker):
    """현재가 조회"""
    return pyupbit.get_orderbook(tickers=ticker)[0]["orderbook_units"][0]["ask_price"]

# 로그인
upbit = pyupbit.Upbit(access, secret)

start_msg = ("[자동매매 시작]")
print(start_msg)

# 시작 메세지 슬랙 전송
post_message(myToken, channel_name, start_msg)

while True:
    try:
        now = datetime.datetime.now()
        start_time = get_start_time({"KRW-" + coin})
        end_time = start_time + datetime.timedelta(days=1)

        if start_time < now < end_time - datetime.timedelta(seconds=10):
            target_price = get_target_price({"KRW-" + coin}, best_k) # K 값
            ma15 = get_ma15({"KRW-" + coin})
            current_price = get_current_price({"KRW-" + coin})
            if target_price < current_price and ma15 < current_price:
                krw = get_balance("KRW")
                if krw > 5000:
                    buy_result = upbit.buy_market_order({"KRW-" + coin}, krw*0.9995)
                    post_message(myToken, channel_name, {coin + "매수 체결: "} + str(buy_result))
        else:
            my_coin = get_balance(coin)
            if my_coin > 0.00008:
                sell_result = upbit.sell_market_order({"KRW-" + coin}, my_coin*0.9995)
                post_message(myToken, channel_name, {coin + "매도 체결 : "} + str(sell_result))
                cash  = upbit.get_balance()
                post_message(myToken, channel_name,"보유현금 : "+ str(cash) + "원")
        time.sleep(1)
    except Exception as e:
        print(e)
        post_message(myToken, channel_name, e)
        time.sleep(1)
