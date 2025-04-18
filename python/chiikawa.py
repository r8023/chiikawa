import requests
from bs4 import BeautifulSoup
import json

# 你的 Discord Webhook URL
DISCORD_WEBHOOK_URL = "https://discordapp.com/api/webhooks/1362859013921837188/8fh5OF3N9XdfXrY3rlQruL83htEUa1Z3fDPMRVdH2STASP-XisUZD59pvLAp5IfKlmuN"

# 存儲爬取過的商品資料
PRODUCT_DATA_FILE = "product_data.json"

def fetch_product_data():
    # 這裡是你的網站 URL，根據實際情況修改
    url = "https://chiikawamarket.jp"
    
    # 發送 GET 請求
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Failed to retrieve data, status code: {response.status_code}")
        return []
    
    print("爬蟲取得吉伊卡哇網站資料")

    # 使用 BeautifulSoup 解析 HTML
    soup = BeautifulSoup(response.content, 'html.parser')

    # 假設商品資料在 class='product' 中
    product_elements = soup.select('.product')

    # 這裡存儲商品資料（名稱、價格等）
    products = []
    for product in product_elements:
        name = product.select_one('.product-name').text.strip()
        price = product.select_one('.product-price').text.strip()

        products.append({
            'name': name,
            'price': price
        })

    return products

def load_previous_data():
    # 嘗試從檔案中讀取上次爬取的資料
    try:
        with open(PRODUCT_DATA_FILE, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return []

def save_data(data):
    # 儲存資料到檔案
    with open(PRODUCT_DATA_FILE, 'w') as file:
        json.dump(data, file)

def compare_data(current_data, previous_data):
    # 比對新舊資料，找出有變動的部分
    new_items = []
    
    current_names = {item['name']: item for item in current_data}
    previous_names = {item['name']: item for item in previous_data}
    
    for name, current_item in current_names.items():
        if name not in previous_names or current_item != previous_names[name]:
            new_items.append(current_item)

    return new_items

def send_discord_notification(new_items):
    # 當有變動時，將變動資料發送到 Discord
    for item in new_items:
        message = f"商品 {item['name']} 有異動，價格：{item['price']}"
        data = {"content": message}
        response = requests.post(DISCORD_WEBHOOK_URL, json=data)
        
        if response.status_code == 204:
            print(f"訊息成功發送：{message}")
        else:
            print(f"發送訊息失敗，狀態碼：{response.status_code}")

def main():
    # 爬取最新的商品資料
    current_data = fetch_product_data()

    # 讀取上次的資料
    previous_data = load_previous_data()

    # 比對資料
    new_items = compare_data(current_data, previous_data)

    # 如果有變動，發送通知
    if new_items:
        send_discord_notification(new_items)

    # 儲存最新資料
    save_data(current_data)

if __name__ == "__main__":
    main()
