import requests

# 你的 Discord Webhook URL
DISCORD_WEBHOOK_URL = "https://discordapp.com/api/webhooks/1363070762843504720/Ade-xxTpUZshFRD9bqqJDOkKerb7kd1lu5FhwgKJ0caD-6xfhYWZvoWiPbmsdeRoWhBt"

# 發送訊息的函數
def send_message_to_discord(message):
    try:
        data = {
            "content": message
        }
        # 發送 POST 請求到 Discord Webhook
        response = requests.post(DISCORD_WEBHOOK_URL, json=data)
        
        # 檢查請求是否成功
        if response.status_code == 204:
            print("訊息成功發送到 Discord！")
        else:
            print(f"發送訊息失敗，狀態碼：{response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"發生錯誤，無法發送訊息到 Discord: {e}")
        send_error_to_discord(f"發送訊息到 Discord 時發生錯誤: {e}")

# 錯誤處理，發送錯誤訊息到 Discord
def send_error_to_discord(error_message):
    try:
        data = {"content": f"錯誤訊息: {error_message}"}
        requests.post(DISCORD_WEBHOOK_URL, json=data)
    except requests.exceptions.RequestException as e:
        print(f"錯誤訊息發送失敗: {e}")

# 主要執行流程
try:
    # 你爬取的程式邏輯
    # 發送訊息
    send_message_to_discord("吉伊卡哇上下架異動")

    # 這裡可以加入其他業務邏輯
    # 例如爬取商品資料等
    
except Exception as e:
    # 捕捉未預期的錯誤，並發送錯誤到 Discord
    error_message = f"發生未知錯誤: {str(e)}"
    print(error_message)
    send_error_to_discord(error_message)
