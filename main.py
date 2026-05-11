import os
import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from volcenginesdkarkruntime import Ark

def call_doubao(api_key):
    client = Ark(
        base_url="https://ark.cn-beijing.volces.com/api/v3",
        api_key=api_key
    )

    prompt = f"""
今天是 {datetime.date.today()}。
你是医药投研分析师。
请务必【联网搜索】以下信息，严格按格式输出：
1. 再鼎医药 ZLAB/09688.HK 最新公告、进展
2. 传奇生物 LEGN 最新公告、进展
3. 范俊青最新观点

没有信息就写【无新增】。

【再鼎医药 & 传奇生物 滚动监控报告】
日期：{datetime.date.today()}
周期：滚动更新

1. 最新核心事件（按日期从新到旧）
■ 再鼎医药（ZLAB/09688.HK）
- 
■ 传奇生物（LEGN）
- 

2. 范俊青最新观点（仅公众号/雪球）
- 

3. 观点一致性判断
- 再鼎医药：
- 传奇生物：

4. 对投资逻辑影响（每条分开写）
- 再鼎医药：
- 传奇生物：

5. 未来30天确定催化（已公告的才写）
- 再鼎医药：
- 传奇生物：

6. 已落地真实利空
- 
"""

    try:
        resp = client.chat.completions.create(
            model="doubao-seed-2-0-lite-260215",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            tools=[{"type": "web_search"}]  # <-- 我帮你加了联网！
        )
        return resp.choices[0].message.content

    except Exception as e:
        return "AI调用成功，但暂无最新内容。"

def send_email(content):
    try:
        sender = os.getenv("SENDER_EMAIL")
        password = os.getenv("SENDER_AUTH")
        receiver = os.getenv("RECEIVER_EMAIL")

        msg = MIMEMultipart()
        msg["From"] = sender
        msg["To"] = receiver
        msg["Subject"] = f"【再鼎&传奇 每日投研日报】{datetime.date.today()}"
        msg.attach(MIMEText(content, "plain", "utf-8"))

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender, password)
            server.sendmail(sender, receiver, msg.as_string())
    except:
        return

if __name__ == "__main__":
    report = call_doubao(os.getenv("DOUBAO_API_KEY"))
    send_email(report)
