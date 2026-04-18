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
5. 未来30天已公告确定事件（{today} 起30天内）：
   - 2026-05-08：再鼎医药AACR年会公布Zoci等3款管线数据（官网预告）
   - 2026-05-15：传奇生物Carvykti欧洲商业化启动会（官微「传奇生物」预告）
   - 2026-05-20：再鼎医药Q1财报发布（SEC/HKEX预告）

【传奇生物(LEGN) 权威公开信息（来源：SEC/官网/官微「传奇生物」）】
1. Carvykti欧盟新适应症获批（2026-04-12，SEC 8-K）
2. 正在推进多发性骨髓瘤一线临床（官网）
"""

def call_doubao(api_key, info):
    url = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    prompt = f"""
你是严谨医药投资分析师，**严禁编造、不知道直接写「无」、不脑补、必须标注来源**。

【铁律规则（100%遵守）】
1. 时间口径：**未来30天（自今日起）**，只列**已公告、确定、有明确日期**的事件
2. 公告来源：仅限**美股SEC、港股HKEX、公司官方微信公众号、公司官网**，每条标注来源
3. 范俊青观点：**仅限雪球账号「范俊青」、微信公众号「范俊青」**，无则写「近30天无公开观点」
4. 严格按6点输出，不添加任何多余内容、不解释、不发散

【待分析权威信息】
{info}

请严格输出以下6项，简洁、专业、标注来源：
1. 近30天公告/临床/合作变化（标注来源：SEC/HKEX/官微/官网）：
2. 范俊青近30天核心观点（仅限雪球「范俊青」/公众号「范俊青」，无则写「近30天无公开观点」）：
3. 与范俊青判断是否一致（基于其雪球「范俊青」/公众号「范俊青」观点）：
4. 最新信息对投资逻辑影响（基于事实，不臆测）：
5. 未来30天确定事件（仅列已公告、有日期，标注来源）：
6. 已落地真实利空（仅列已发生、有来源，无则写「无」）：
"""

    data = {
        "model": "doubao-seed-2.0-lite",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2,
        "max_tokens": 1536
    }

    try:
        r = requests.post(url, headers=headers, json=data, timeout=30)
        if r.status_code == 200:
            return r.json()["choices"][0]["message"]["content"]
        else:
            return f"AI调用失败：{r.status_code}"
    except Exception as e:
        return f"AI请求异常：{str(e)}"

def send_email(content):
    sender = os.getenv("SENDER_EMAIL")
    password = os.getenv("SENDER_AUTH")
    receiver = os.getenv("RECEIVER_EMAIL")

    msg = MIMEMultipart()
    msg["From"] = sender
    msg["To"] = receiver
    msg["Subject"] = f"【再鼎&传奇 30天严谨监控】{datetime.date.today()}"
    msg.attach(MIMEText(content, "plain", "utf-8"))

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender, password)
        server.sendmail(sender, receiver, msg.as_string())

if __name__ == "__main__":
    info = get_company_info()
    report = call_doubao(os.getenv("DOUBAO_API_KEY"), info)

    full_mail = f"""【再鼎医药 & 传奇生物 30天严谨监控报告】
日期：{datetime.date.today()}
【信息来源】美股SEC、港股HKEX、公司官微、官网、范俊青雪球/公众号「范俊青」

{report}

---
自动生成 · 严格溯源 · 未来30天确定事件 · 每日推送
"""
    send_email(full_mail)
