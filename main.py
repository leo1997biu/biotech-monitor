import os
import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from volcenginesdkarkruntime import Ark

def get_company_info():
    today = datetime.date.today()
    return f"""
【再鼎医药(ZLAB,09688.HK) 权威公开信息】
来源：SEC、HKEX、微信公众号「再鼎医药」、公司官网
1. 2026-04-10（HKEX公告）：Z-201 III期临床ORR 45%，拟申报NDA
2. 2026-04-12（SEC 8-K/官网）：Carvykti获欧盟EMA新适应症批准
3. 2026-04-15（官微「再鼎医药」）：与勃林格殷格翰达成DLL3联合疗法临床合作
4. 2026-04-16（HKEX公告）：与安进达成Zoci全球临床合作
5. 2026-04-18（官微「再鼎医药」+ AACR）：Zoci小细胞肺癌脑转移ORR 56%，神经内分泌癌ORR 42%，2026年将启动3项全球注册III期临床

【传奇生物(LEGN) 权威公开信息】
来源：SEC、官网、官微「传奇生物」
1. 2026-04-12（SEC 8-K）：Carvykti欧盟新适应症获批

【范俊青公开观点】
来源：公众号「范俊青」2026-04-18
1. 再鼎医药Zoci基石药物格局初步形成；2026年多项全球III期临床并行，短期亏损扩大是研发加速的正面信号；公司进入全球自主管线价值重估阶段
"""

def call_doubao(api_key, info):
    client = Ark(
        base_url="https://ark.cn-beijing.volces.com/api/v3",
        api_key=api_key
    )

    # === 这是你最终版超强提示词，不会丢信息、格式完美 ===
    prompt = f"""
你是专业医药投研分析师，只根据提供的信息整理，严禁编造，不知道写“无”。

【信息来源】
SEC公告、港交所HKEX、公司官网、微信公众号、AACR、范俊青（公众号+雪球）

【输出要求】
1. 简洁、清晰、分点、易读
2. 关键数据加粗，如**56%**
3. 必须标注来源
4. 无内容必须写“无”，不能空
5. 按下面固定格式输出

==================================================
【信息】
{info}
==================================================

【输出格式】
【再鼎医药 & 传奇生物 滚动监控报告】
日期：{datetime.date.today()}
周期：近7天滚动跟踪

1. 近7天核心进展（来源标注清晰）
   再鼎医药（ZLAB/09688.HK）
   - （来源）：内容
   传奇生物（LEGN）
   - （来源）：内容

2. 范俊青近7天核心观点
   - 内容（来源）

3. 与范俊青判断是否一致
   - 结论

4. 最新信息对投资逻辑影响
   - 再鼎医药：
   - 传奇生物：

5. 未来30天已公告确定事件
   - 再鼎医药：
   - 传奇生物：

6. 已落地真实利空
   - 无/具体内容
"""

    try:
        completion = client.chat.completions.create(
            model="doubao-seed-2-0-lite-260215",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"调用异常: {str(e)}"

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
    info = get_company_info()
    report = call_doubao(os.getenv("DOUBAO_API_KEY"), info)
    send_email(report)
