import requests
import json
import os
import time
import re
from datetime import datetime
import pprint

SLEEP_SEC = 0.5
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
}

COLOR_DEFAULT = 16777168

def load_previous_products(file_path):
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
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

def save_products(file_path, products):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(products, f, ensure_ascii=False, indent=2)

def get_all_products(base_url, headers, sleep_sec=0.5):
    all_products = []
    page = 1
    while True:
        url = f"{base_url}/products.json?page={page}"
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
                    try:
                        restock_dt = datetime.strptime(match.group(1), "%Y%m%d")
                        if restock_dt.date() > datetime.now().date():
                            restock_date = restock_dt.strftime("%Y-%m-%d")
                            break
                    except ValueError:
                        continue
            product = {
                "id": p["id"],
                "title": p["title"],
                "price": p["variants"][0]["price"],
                "url": f"{base_url}/products/{p['handle']}",
                "image": p["images"][0] if p["images"] else None,
                "variant_ids": [v["id"] for v in p["variants"]],
                "available": p["variants"][0]["available"]
            }
            if restock_date:
                product["restock_date"] = restock_date
                
            all_products.append(product)
        page += 1
        time.sleep(sleep_sec)
    return all_products

def find_diff_products(old, new):
    old_map = {p["id"]: p for p in old}
    new_map = {p["id"]: p for p in new}

    new_items = [p for id_, p in new_map.items() if id_ not in old_map]
    removed_items = [p for id_, p in old_map.items() if id_ not in new_map]
    restocked_items = []
    for id_, new_p in new_map.items():
        old_p = old_map.get(id_)
        if old_p and not old_p.get("available") and new_p.get("available"):
            restocked_items.append(new_p)
    upcoming_restocks = [p for p in new_map.values() if not p["available"] and p.get("restock_date")]
    return new_items, removed_items, restocked_items, upcoming_restocks

def load_notified_list(file_path):
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return {str(p["id"]): p for p in json.load(f)}
        except Exception as e:
            print(f"⚠️ 載入快照檔失敗：{e}")
            return {}
    return {}

def save_notified_list(file_path, items):
    item = {
        str(p["id"]): {
            "id": p["id"],
            "available": p.get("available"),
            "restock_date": p.get("restock_date")
        } for p in items
    }
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(item, f, ensure_ascii=False, indent=2)

def has_item_change(old, new):
    keys = ["available", "restock_date"]
    return any(old.get(k) != new.get(k) for k in keys)

def filter_changed(items):
    result = []
    for p in items:
        old = notified_list.get(str(p["id"]))
        if not old or has_significant_change(old, p):
            result.append(p)
    return result

def send_discord_embeds(webhook_url, items, action_title, color=COLOR_DEFAULT):
    if not webhook_url:
        print("❗️ 沒有設定 Webhook URL，跳過發送")
        return
    embeds = []
    for index, item in enumerate(items):
        title = f"{index+1}. {item['title'][:256]}"
        description = f"💰 價格：¥{item['price']}\n\n🤍 ID：{', '.join(map(str, item['variant_ids']))}"
        if item.get("restock_date"):
            description = f"🔖 補貨日期：{item['restock_date']}\n\n" + description
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
            "content": action_title,
            "embeds": embeds[i:i + 10]
        }
        while True:
            try:
                res = requests.post(webhook_url, json=payload)
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
