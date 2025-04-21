import requests
import json
import time
import os

BASE_URL = "https://chiikawamarket.jp"
PRODUCTS_URL = f"{BASE_URL}/collections/all/products.json"
SLEEP_SEC = 0.5
DATA_DIR = "data"
OUTPUT_FILE = os.path.join(DATA_DIR, "products.json")

DISCORD_WEBHOOK_URL = "https://discordapp.com/api/webhooks/1363070762843504720/Ade-xxTpUZshFRD9bqqJDOkKerb7kd1lu5FhwgKJ0caD-6xfhYWZvoWiPbmsdeRoWhBt"


def load_previous_products():
    if os.path.exists(OUTPUT_FILE):
        try:
            with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if not content:
                    return []
                return json.loads(content)
        except Exception as e:
            print(f"⚠️ 載入歷史檔案失敗：{e}")
            return []
    return []

def get_all_products():
    all_products = []
    page = 1

    while True:
        url = f"{PRODUCTS_URL}?page={page}"
        print(f"抓取第 {page} 頁：{url}")
        res = requests.get(url)
        if res.status_code != 200:
            print(f"⚠️ 第 {page} 頁請求失敗，狀態碼 {res.status_code}")
            break

        data = res.json()
        products = data.get("products", [])
        if not products:
            print("🛑 沒有更多商品，提早結束")
            break

        for p in products:
            product = {
                "id": p["id"],
                "title": p["title"],
                "price": p["variants"][0]["price"],
                "url": f"{BASE_URL}/products/{p['handle']}",
                "image": p["images"][0] if p["images"] else None,
                "variant_ids": [v["id"] for v in p["variants"]]
            }
            all_products.append(product)

        page += 1
        time.sleep(SLEEP_SEC)

    return all_products

def load_previous_products():
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_products(products):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(products, f, ensure_ascii=False, indent=2)

def find_diff_products(old, new):
    old_map = {p["id"]: p for p in old}
    new_map = {p["id"]: p for p in new}

    new_items = [p for id_, p in new_map.items() if id_ not in old_map]
    removed_items = [p for id_, p in old_map.items() if id_ not in new_map]

    return new_items, removed_items

def send_discord_message(content):
    if not DISCORD_WEBHOOK_URL:
        print("❗️ 沒有設定 Webhook URL，跳過發送")
        return
    try:
        res = requests.post(DISCORD_WEBHOOK_URL, json={"content": content})
        if res.status_code != 204:
            print(f"❗️ 發送 Discord 失敗：{res.status_code} {res.text}")
    except Exception as e:
        print(f"❗️ Discord 發送錯誤：{e}")

def main():
    print("🚀 開始抓取所有商品...")
    new_products = get_all_products()
    print(f"📦 共抓到 {len(new_products)} 件商品")

    old_products = load_previous_products()
    new_items, removed_items = find_diff_products(old_products, new_products)

    print(f"✨ 新增商品：{len(new_items)}")
    print(f"🔻 下架商品：{len(removed_items)}")

    if new_items or removed_items:
        message_lines = ["📦 Chiikawa 商品更新通知"]

        if new_items:
            message_lines.append(f"\n✨ 新增商品（{len(new_items)} 件）：")
            for item in new_items:
                message_lines.append(f"- {item['title']} | ¥{item['price']}")
                message_lines.append(f"  🔗 {item['url']}")
                message_lines.append(f"  🤍 Variants: {item['variant_ids']}")

        if removed_items:
            message_lines.append(f"\n🔻 下架商品（{len(removed_items)} 件）：")
            for item in removed_items:
                message_lines.append(f"- {item['title']} | ¥{item['price']}")
                message_lines.append(f"  🔗 {item['url']}")
                message_lines.append(f"  🤍 Variants: {item['variant_ids']}")

        send_discord_message("\n".join(message_lines))
    else:
        send_discord_message("📦 Chiikawa 商品更新通知\n✨ 新增商品：0\n🔻 下架商品：0")

    save_products(new_products)

if __name__ == "__main__":
    main()
