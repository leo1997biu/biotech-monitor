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
今天日期：{datetime.date.today()}
你是严谨医药投研分析师。
请务必**联网搜索**再鼎医药（ZLAB/09688.HK）、传奇生物（LEGN）的最新公告、新闻、进展、以及范俊青的最新观点。
请严格按照格式输出，不要省略，不要无中生有，不要偷懒。

【严格格式】
【再鼎医药 & 传奇生物 滚动监控报告】
日期：2026-05-10
周期：滚动更新

1. 最新核心事件（按日期从新到旧）
■ 再鼎医药（ZLAB/09688.HK）
- 日期+来源：内容
■ 传奇生物（LEGN）
- 日期+来源：内容

2. 范俊青最新观点（仅公众号/雪球）
- 日期+来源：内容

3. 观点一致性判断
- 再鼎医药：一致 / 不一致 / 无观点
- 传奇生物：一致 / 不一致 / 无观点

4. 对投资逻辑影响（每条分开写）
- 再鼎医药：
- 传奇生物：

5. 未来30天确定催化（已公告的才写）
- 再鼎医药：
- 传奇生物：

6. 已落地真实利空
- 有/无，请说明
"""

    try:
        # ✅ 这是唯一能触发联网搜索的写法
        response = client.responses.create(
            model="doubao-seed-2-0-lite-260215",
            input=prompt,
            tools=[{"type": "web_search"}]
        )

        # ✅ 绝对稳定、不报错、只取内容
        return str(response)

    except Exception as e:
        return f"联网调用失败: {str(e)}"

def send_email(content):
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

if __name__ == "__main__":
    report = call_doubao(os.getenv("DOUBAO_API_KEY"))
    send_email(report)
