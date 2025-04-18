import requests

# 你的 Discord Webhook URL
DISCORD_WEBHOOK_URL = "https://discordapp.com/api/webhooks/1362859013921837188/8fh5OF3N9XdfXrY3rlQruL83htEUa1Z3fDPMRVdH2STASP-XisUZD59pvLAp5IfKlmuN"

# 要發送的訊息
data = {
    "content": "吉伊卡哇上下架異動"
}

# 發送 POST 請求到 Discord Webhook
response = requests.post(DISCORD_WEBHOOK_URL, json=data)

# 檢查請求是否成功
if response.status_code == 204:
    print("訊息成功發送到 Discord！")
else:
    print(f"發送訊息失敗，狀態碼：{response.status_code}")
