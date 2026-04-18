import os
import smtplib
import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def generate_report():
    today = datetime.date.today()
    one_week_ago = today - datetime.timedelta(days=7)
    
    content = f"""【再鼎医药 & 传奇生物 每日监控报告】
日期：{today}

1. 近一周公告/临床/合作变化：
待AI自动更新

2. 范俊青近一周核心观点：
待AI自动更新

3. 与范俊青判断是否一致：
待AI自动更新

4. 最新信息对逻辑影响：
待AI自动更新

5. 未来7天确定事件：
待AI自动更新

6. 已落地真实利空：
待AI自动更新
"""
    return content

def send_email(content):
    sender = os.getenv("SENDER_EMAIL")
    app_password = os.getenv("SENDER_AUTH")
    receiver = os.getenv("RECEIVER_EMAIL")

    msg = MIMEMultipart()
    msg["From"] = sender
    msg["To"] = receiver
    msg["Subject"] = f"【自动报告】再鼎&传奇 {datetime.date.today()}"
    msg.attach(MIMEText(content, "plain", "utf-8"))

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender, app_password)
        server.sendmail(sender, receiver, msg.as_string())

if __name__ == "__main__":
    report = generate_report()
    send_email(report)
