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
你是严谨医药投研分析师，绝对不允许偷懒、不允许概括、不省略信息。请先联网搜索最新资讯！

【严格规则】
1. 必须逐条列出所有事件，不许合并、不许简写
2. 必须标注日期+来源，缺一不可
3. 必须区分：再鼎医药 / 传奇生物，不能混在一起
4. 必须按时间从新到旧排列
5. 没有新内容就写“无新增”，不许空着
6. 严禁重复、严禁编造、严禁用相同回答敷衍

【信息来源仅限】
SEC、HKEX、公司官网、微信公众号（再鼎医药、传奇生物）、范俊青公众号/雪球、AACR

【必须严格按以下格式输出，一字不差】
【再鼎医药 & 传奇生物 滚动监控报告】
日期：{datetime.date.today()}
周期：滚动更新

1. 最新核心事件（按日期从新到旧）
■ 再鼎医药（ZLAB/09688.HK）
- 日期+来源：具体内容
■ 传奇生物（LEGN）
- 日期+来源：具体内容

2. 范俊青最新观点（仅公众号/雪球）
- 日期+来源：具体观点

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
- 有/无，如有请写日期+来源+内容
"""

    try:
        completion = client.responses.create(
            model="doubao-seed-2-0-lite-260215",
            input=[{"role": "user", "content": prompt}],
            tools=[{"type": "web_search"}]
        )

        # --------------------------
        # 只保留 100% 稳定的 Token 统计
        # --------------------------
        usage = completion.usage
        prompt_tokens = usage.prompt_tokens
        completion_tokens = usage.completion_tokens
        total_tokens = usage.total_tokens

        # 成本计算
        token_cost = (prompt_tokens * 0.004 / 1000) + (completion_tokens * 0.008 / 1000)

        cost_info = f"""

---
【本次消耗】
Prompt Tokens: {prompt_tokens}
Completion Tokens: {completion_tokens}
Total Tokens: {total_tokens}
Token成本: {token_cost:.4f} 元
"""

        return completion.output_text + cost_info

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
    report = call_doubao(os.getenv("DOUBAO_API_KEY"))
    send_email(report)
