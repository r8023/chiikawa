import requests
import json
import time
import os
import pprint
import re
from datetime import datetime

BASE_URL = "https://nagano-market.jp"
PRODUCTS_URL = f"{BASE_URL}/collections/all/products.json"
SLEEP_SEC = 0.5
DATA_DIR = "data"
OUTPUT_FILE = os.path.join(DATA_DIR, "products_nagano.json")

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
}

DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1363910496348143666/Gzy32rFsnGew9M_LHhhdUmyHgr9zBU4u_TA0c_5UQDvYEUCWCj6MXSsHYTZlNMXBwDAM"

COLOR_DEFAULT = 16777168
COLOR_UPCOMING = 16761035

def load_previous_products():
    if os.path.exists(OUTPUT_FILE):
        try:
            with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if not content:
                    print("⚠️ 歷史檔案為空")
                    return []
                return json.loads(content)
        except Exception as e:
            print(f"⚠️ 載入歷史檔案失敗：{e}")
            print(f"⚠️ 檔案內容：{content[:100]}...")
            return []
    return []

def get_all_products():
    all_products = []
    page = 1

    while True:
        url = f"{PRODUCTS_URL}?page={page}"
        print(f"抓取第 {page} 頁：{url}")

        try:
            res = requests.get(url, headers=headers)
        except Exception as e:
            print(f"⚠️ 發送請求失敗：{e}")
            return None

        if res.status_code != 200:
            print(f"⚠️ 第 {page} 頁請求失敗，狀態碼 {res.status_code}")
            return None

        data = res.json()
        products = data.get("products", [])
        if not products:
            print("🛑 沒有更多商品，結束")
            break

        for p in products:
            tags = p.get("tags", [])
            restock_date = None
            for tag in tags:
                match = re.search(r"RE(\d{8})", tag)
                if match:
                    date_str = match.group(1)
                    try:
                        restock_dt = datetime.strptime(date_str, "%Y%m%d")
                        if restock_dt.date() > datetime.now().date():  # 只保留未來的日期
                            restock_date = restock_dt.strftime("%Y-%m-%d")
                            break
                    except ValueError:
                        continue  # 萬一日期不合法，就跳過

            product = {
                "id": p["id"],
                "title": p["title"],
                "price": p["variants"][0]["price"],
                "url": f"{BASE_URL}/products/{p['handle']}",
                "image": p["images"][0] if p["images"] else None,
                "variant_ids": [v["id"] for v in p["variants"]],
                "available": p["variants"][0]["available"],
                "restock_date": restock_date
            }
            all_products.append(product)

        page += 1
        time.sleep(SLEEP_SEC)

    return all_products

def save_products(products):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(products, f, ensure_ascii=False, indent=2)

def find_diff_products(old, new):
    old_map = {p["id"]: p for p in old}
    new_map = {p["id"]: p for p in new}

    new_items = [p for id_, p in new_map.items() if id_ not in old_map]
    removed_items = [p for id_, p in old_map.items() if id_ not in new_map]

    restocked_items = []
    for id_, new_p in new_map.items():
        old_p = old_map.get(id_)
        if old_p and old_p.get("available") == False and new_p.get("available") == True:
            restocked_items.append(new_p)

    # ✅ 預測補貨清單：available=False 且包含 restock_date
    upcoming_restocks = [p for p in new_map.values() if not p["available"] and p.get("restock_date")]

    return new_items, removed_items, restocked_items, upcoming_restocks

def main():
    print("🚀 開始抓取所有商品...")
    new_products = get_all_products()

    if new_products is None:
        print("❌ 商品資料抓取失敗，中止比對")
        return

    print(f"🪄 共抓到 {len(new_products)} 件商品")

    old_products = load_previous_products()
    new_items, removed_items, restocked_items, upcoming_restocks = find_diff_products(old_products, new_products)

    print(f"✨ 新增商品：{len(new_items)}")
    print(f"🔻 下架商品：{len(removed_items)}")
    print(f"🧃 補貨商品：{len(restocked_items)}")
    print(f"🔖 預計補貨商品：{len(upcoming_restocks)}")

    if new_items or removed_items or restocked_items or upcoming_restocks:
        if new_items:
            send_discord_embeds(new_items, f"\n✨ 新增商品：{len(new_items)}")

        if removed_items:
            send_discord_embeds(removed_items, f"\n🔻 下架商品：{len(removed_items)}")

        if restocked_items:
            send_discord_embeds(restocked_items, f"\n🧃 補貨商品：{len(restocked_items)}")

        if upcoming_restocks:
            send_discord_embeds(upcoming_restocks, f"\n🔖 預計補貨商品：{len(upcoming_restocks)}", color=COLOR_UPCOMING)
    else:
        requests.post(DISCORD_WEBHOOK_URL, json={"content": "✨ 新增商品：0\n🔻 下架商品：0\n🧃 補貨商品：0\n🔖 預計補貨商品：0"})

    save_products(new_products)

def send_discord_embeds(items, action_title, color=COLOR_DEFAULT):
    if not DISCORD_WEBHOOK_URL:
        print("❗️ 沒有設定 Webhook URL，跳過發送")
        return

    embeds = []

    for index, item in enumerate(items):
        title = f"{index+1}. {item['title'][:256]}"
        description = f"💰 價格：¥{item['price']}\n\n🤍 ID：{', '.join(map(str, item['variant_ids']))}"

        if item.get("restock_date"):
            description = f"🔖 預計補貨日：{item['restock_date']}\n\n" + description

        if len(description) > 2048:
            description = description[:2045] + "..."

        embed = {
            "title": title,
            "url": item["url"],
            "description": description,
            "color": color
        }

        if item.get("image") and isinstance(item["image"], dict) and "src" in item["image"]:
            embed["thumbnail"] = {"url": item["image"]["src"]}

        embeds.append(embed)

    for i in range(0, len(embeds), 10):
        payload = {
            "content": f"{action_title}",
            "embeds": embeds[i:i + 10]
        }

        while True:
            try:
                res = requests.post(DISCORD_WEBHOOK_URL, json=payload)
                if res.status_code in [200, 204]:
                    break
                elif res.status_code == 429:
                    retry_after = res.json().get("retry_after", 1)
                    print(f"⏳ 被限流，等待 {retry_after:.2f} 秒後重試")
                    time.sleep(retry_after)
                else:
                    print(f"❗️ 發送 Discord Embed 失敗：{res.status_code} {res.text}")
                    break
            except Exception as e:
                pprint.pprint(payload)
                print(f"❗️ Discord 發送錯誤：{e}")
                break

        time.sleep(0.5)

if __name__ == "__main__":
    main()
