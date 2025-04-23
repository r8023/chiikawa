import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from general import *

#變動參數
type = "chiikawa"
BASE_URL = "https://chiikawamarket.jp"
DISCORD_WEBHOOK_URL = "https://discordapp.com/api/webhooks/1363070762843504720/Ade-xxTpUZshFRD9bqqJDOkKerb7kd1lu5FhwgKJ0caD-6xfhYWZvoWiPbmsdeRoWhBt"

#固定參數
DATA_DIR = "data"
DATA_FILE = f"data/products_{type}.json"
NOTIFIED_FILE = f"data/notified_{type}.json"
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
    print(f"🔖 即將補貨商品：{len(upcoming)}")

    #上一次已通知過的
    last_notified_ids = load_last_notified_ids(NOTIFIED_FILE)
    new_items = [p for p in new_items if p["id"] not in last_notified_ids]
    removed_items = [p for p in removed_items if p["id"] not in last_notified_ids]
    restocked_items = [p for p in restocked_items if p["id"] not in last_notified_ids]
    upcoming = [p for p in upcoming if p["id"] not in last_notified_ids]

    print(f"=== 未發送過通知 ===")
    print(f"✨ 新增商品：{len(new_items)}")
    print(f"🔻 下架商品：{len(removed_items)}")
    print(f"🧃 補貨商品：{len(restocked_items)}")
    print(f"🔖 即將補貨商品：{len(upcoming)}")

    if new_items:
        send_discord_embeds(DISCORD_WEBHOOK_URL, new_items, f"\n✨ 新增商品：{len(new_items)}")
    if removed_items:
        send_discord_embeds(DISCORD_WEBHOOK_URL, removed_items, f"\n🔻 下架商品：{len(removed_items)}")
    if restocked_items:
        send_discord_embeds(DISCORD_WEBHOOK_URL, restocked_items, f"\n🧃 補貨商品：{len(restocked_items)}")
    if upcoming:
        send_discord_embeds(DISCORD_WEBHOOK_URL, upcoming, f"\n🔖 即將補貨商品：{len(upcoming)}", color=COLOR_UPCOMING)
    
    save_products(DATA_FILE, new_products)

    notified_this_round = set(
        p["id"] for p in new_items + removed_items + restocked_items + upcoming
    )
    save_last_notified_ids(NOTIFIED_FILE, notified_this_round)

if __name__ == "__main__":
    main()
