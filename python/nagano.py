import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from general import *

#變動參數
type = "nagano"
BASE_URL = "https://nagano-market.jp"
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL_NAGANO")

#固定參數 
DATA_DIR = "data"
DATA_FILE = f"data/products_{type}.json"
NOTIFIED_FILE = f"data/notified_{type}.json"
PRODUCTS_URL = f"{BASE_URL}/collections/all/products.json"
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
}

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
    print(f"🛒 即將補貨商品：{len(upcoming)}")

    #上一次已通知過的
    notified_list = load_notified_map(NOTIFIED_FILE)
    #new_items = filter_changed(new_items,notified_list)
    #removed_items = filter_changed(removed_items,notified_list)
    restocked_items = filter_changed(restocked_items,notified_list)
    upcoming = filter_changed(upcoming,notified_list)

    print(f"=== 未發送過通知 ===")
    print(f"🧃 補貨商品：{len(restocked_items)}")
    print(f"🛒 即將補貨商品：{len(upcoming)}")

    if new_items:
        send_discord_embeds(DISCORD_WEBHOOK_URL, new_items, f"\n✨ 新增商品：{len(new_items)}")
    if removed_items:
        send_discord_embeds(DISCORD_WEBHOOK_URL, removed_items, f"\n🔻 下架商品：{len(removed_items)}", color=10824191)
    if restocked_items:
        send_discord_embeds(DISCORD_WEBHOOK_URL, restocked_items, f"\n🧃 補貨商品：{len(restocked_items)}",color=16761035)
    if upcoming:
        send_discord_embeds(DISCORD_WEBHOOK_URL, upcoming, f"\n🛒 即將補貨商品：{len(upcoming)}", color=16761035)
    
    save_products(DATA_FILE, new_products)

    save_notified_map(NOTIFIED_FILE, new_items + removed_items + restocked_items + upcoming)

if __name__ == "__main__":
    main()
