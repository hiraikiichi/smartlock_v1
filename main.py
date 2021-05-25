import gc
import ssl
import esp
import time
import socket
import network
from machine import Pin,PWM
from utime import sleep_ms, ticks_ms


gc.collect()
esp.osdebug(None)

ssid = 'SSIDをここに入力'
password = 'パスワードをここに入力'

station = network.WLAN(network.STA_IF)
station.active(True)
station.connect(ssid, password)

# ピン指定
ledpin = 32
servo = 13

led = Pin(ledpin, Pin.OUT)
servo1 = PWM(Pin(servo), freq = 100)

def web_page():
    
    if led.value() == 1:
        gpio_state="OPEN"
    else:
        gpio_state="CLOSE"
    
    html = """
    <html lang = "ja">
    <head>
    <title>Key</title>
    <meta charset="UTF-8" name="viewport" content="width=device-width, initial-scale=1">
    <link rel="icon" href="data:,">
    <style>
      html{font-family: Helvetica; display:inline-block; margin: 0px auto; text-align: center;}
    h1{color: #0F3376; padding: 2vh;}p{font-size: 1.5rem;}.button{display: inline-block; background-color: #e7bd3b; border: none;
    border-radius: 4px; color: white; padding: 16px 40px; text-decoration: none; font-size: 30px; margin: 2px; cursor: pointer;}
    .button2{background-color: #4286f4;}
    </style>
    </head>
    <body>
    <h1>かぎ</h1>
    <p>now: <strong>""" + gpio_state + """</strong></p>
    <p><a href="/?led=on"><button class="button">OPEN</button></a></p>
    <p><a href="/?led=off"><button class="button button2">CLOSE</button></a></p>
    </body>
    </html>
   """
    return html

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# 接続待ちするIpアドレスとポート番号指定
s.bind(('', 80))
# 接続を待つ,サーバー受け入れ最大数
s.listen(5)

def open():
    se = socket.socket()
    ai = socket.getaddrinfo("slack.com", 443)
    addr = ai[0][-1]
    se.connect(addr)
    se = ssl.wrap_socket(se)
    send_data = "token=【Slackのトークン】&channel=%23【チャンネル名】&text=Opend the lab from ESP32"
    se.write(b"POST /api/chat.postMessage HTTP/1.1\r\n")
    se.write(b"Host: slack.com\r\n")
    se.write(b"Accept: */*\r\n")
    se.write(b"Content-Length: %d\r\n" % len(send_data))
    se.write(b"Content-Type: application/x-www-form-urlencoded\r\n")
    se.write(b"Connection: close\r\n")
    se.write(b"\r\n")
    se.write(send_data)
    se.close()
    led.on()
    servo1.duty(240)
    time.sleep_ms(2000)
    servo1.duty(150)
    time.sleep_ms(2000)

def close():
    se = socket.socket()
    ai = socket.getaddrinfo("slack.com", 443)
    addr = ai[0][-1]
    se.connect(addr)
    se = ssl.wrap_socket(se)
    send_data = "token=【Slackのトークン】&channel=%23lab_open&text=Closed the lab from ESP32"
    se.write(b"POST /api/chat.postMessage HTTP/1.1\r\n")
    se.write(b"Host: slack.com\r\n")
    se.write(b"Accept: */*\r\n")
    se.write(b"Content-Length: %d\r\n" % len(send_data))
    se.write(b"Content-Type: application/x-www-form-urlencoded\r\n")
    se.write(b"Connection: close\r\n")
    se.write(b"\r\n")
    se.write(send_data)
    se.close()
    led.off()
    servo1.duty(60)
    time.sleep_ms(2000)
    servo1.duty(150)
    time.sleep_ms(2000)

while True:
    # 接続を受け付ける
    # 誰かがアクセスしてきたら、コネクションとアドレスを入れる
    conn, addr = s.accept()
    # byte形式で通信を行う
    # データを受け取る
    request = conn.recv(1024)
    request = str(request)
    led_on = request.find('/?led=on') #o
    led_off = request.find('/?led=off') #o

    if led_on == 6:
        open()
    if led_off == 6:
        close()

    response = web_page()
    conn.send('HTTP/1.1 200 OK\n')
    conn.send('Content-Type: text/html\n')
    conn.send('Connection: close\n\n')
    conn.sendall(response)
    conn.close()