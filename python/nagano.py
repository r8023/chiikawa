import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from general import *

#變動參數
type = "nagano"
BASE_URL = "https://nagano-market.jp"
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1363910496348143666/Gzy32rFsnGew9M_LHhhdUmyHgr9zBU4u_TA0c_5UQDvYEUCWCj6MXSsHYTZlNMXBwDAM"

#固定參數 
DATA_DIR = "data"
DATA_FILE = f"data/products_{type}.json"
PRODUCTS_URL = f"{BASE_URL}/collections/all/products.json"
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
}
COLOR_UPCOMING = 16761035

def main():
    print(f"🚀 {type} 抓取開始...")
    new_products = get_all_products(f"{BASE_URL}/collections/all", headers)
    if new_products is None:
        return
    old_products = load_previous_products(DATA_FILE)
    new_items, removed_items, restocked_items, upcoming = find_diff_products(old_products, new_products)

    print(f"✨ 新增商品：{len(new_items)}")
    print(f"🔻 下架商品：{len(removed_items)}")
    print(f"🧃 補貨商品：{len(restocked_items)}")
    print(f"🔖 預計補貨商品：{len(upcoming)}")

    if new_items:
        send_discord_embeds(DISCORD_WEBHOOK_URL, new_items, f"\n✨ 新增商品：{len(new_items)}")
    if removed_items:
        send_discord_embeds(DISCORD_WEBHOOK_URL, removed_items, f"\n🔻 下架商品：{len(removed_items)}")
    if restocked_items:
        send_discord_embeds(DISCORD_WEBHOOK_URL, restocked_items, f"\n🧃 補貨商品：{len(restocked_items)}")
    if upcoming:
        send_discord_embeds(DISCORD_WEBHOOK_URL, upcoming, f"\n🔖 預計補貨商品：{len(upcoming)}", color=COLOR_UPCOMING)
    if not (new_items or removed_items or restocked_items or upcoming):
        requests.post(DISCORD_WEBHOOK_URL, json={"content": "✨ 新增商品：0\n🔻 下架商品：0\n🧃 補貨商品：0\n🔖 預計補貨商品：0"})

    save_products(DATA_FILE, new_products)

if __name__ == "__main__":
    main()
