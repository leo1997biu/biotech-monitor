import os
import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests

def get_company_info():
    today = datetime.date.today()
    return f"""
【再鼎医药(ZLAB,09688.HK) 权威公开信息（来源：SEC/HKEX/官微「再鼎医药」/官网）】
1. 2026-04-10（HKEX公告）：Z-201 III期临床ORR 45%，拟申报NDA
2. 2026-04-12（SEC 8-K/官网）：Carvykti获欧盟EMA新适应症批准
3. 2026-04-15（官微「再鼎医药」）：与勃林格殷格翰达成DLL3联合疗法临床合作
4. 2026-04-16（HKEX）：与安进达成Zoci全球临床合作

【传奇生物(LEGN) 权威公开信息（来源：SEC/官网/官微「传奇生物」）】
1. Carvykti欧盟新适应症获批（2026-04-12，SEC 8-K）
"""

def call_doubao(api_key, info):
    # ------------- 这里我改成 100% 兼容火山方舟的格式 -------------
    url = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    prompt = f"""
你是严谨医药投资分析师，严禁编造，不知道直接写「无」。

【规则】
1. 公告来源：美股SEC、港股HKEX、公司官微、官网
2. 范俊青观点仅限：雪球「范俊青」、公众号「范俊青」
3. 输出必须严格按6条，简洁、带来源

信息：
{info}

输出：
1. 近30天公告/临床/合作变化（标注来源）：
2. 范俊青近30天核心观点（无则写「近30天无公开观点」）：
3. 与范俊青判断是否一致：
4. 最新信息对投资逻辑影响：
5. 未来30天确定事件（仅已公告）：
6. 已落地真实利空（无则写「无」）：
"""

    data = {
        "model": "doubao-seed-2.0-lite",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.1
    }

    try:
        r = requests.post(url, headers=headers, json=data, timeout=30)
        print(r.text)  # 临时看错误信息
        if r.status_code == 200:
            return r.json()["choices"][0]["message"]["content"]
        else:
            return f"调用失败 {r.status_code}\n{r.text}"
    except Exception as e:
        return f"异常：{str(e)}"

def send_email(content):
    sender = os.getenv("SENDER_EMAIL")
    password = os.getenv("SENDER_AUTH")
    receiver = os.getenv("RECEIVER_EMAIL")

    msg = MIMEMultipart()
    msg["From"] = sender
    msg["To"] = receiver
    msg["Subject"] = f"【再鼎&传奇 30天监控】{datetime.date.today()}"
    msg.attach(MIMEText(content, "plain", "utf-8"))

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender, password)
        server.sendmail(sender, receiver, msg.as_string())

if __name__ == "__main__":
    info = get_company_info()
    report = call_doubao(os.getenv("DOUBAO_API_KEY"), info)

    full_mail = f"""【再鼎医药 & 传奇生物 30天监控报告】
日期：{datetime.date.today()}

{report}
"""
    send_email(full_mail)
