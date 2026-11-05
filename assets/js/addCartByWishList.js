
const existing = document.querySelector(
    'script[src="https://r8023.github.io/chiikawa/assets/js/addCartByList.js"]'
);

if (existing) {
    existing.remove();
}

const scriptTR = document.createElement("script");
scriptTR.src = "https://r8023.github.io/chiikawa/assets/js/general.js";

scriptTR.onload = () => {

    const buttons = $(".gw-wl-product-list .gw-wl-product-card__action-btn");
    const total = buttons.length;

    if (total === 0) {
        showToast("收藏列表沒有找到商品", "warning");
        return;
    }

    showToast(`找到 ${total} 個收藏商品，開始依序加入購物車`, "success");

    let completed = 0;

    buttons.each(function (index) {
        const $btn = $(this);

        setTimeout(() => {
            const name = $btn.closest(".gw-wl-product-card").find("a").first().text().trim()
                || `商品 ${index + 1}`;

            showToast(
                `[${index + 1}/${total}] 正在處理：${name}`,
                "info"
            );

            try {
                $btn.trigger("click");
                completed++;

                if (completed === total) {
                    setTimeout(() => {
                        showToast(
                            `執行完成！已點擊 ${completed}/${total} 個商品`,
                            "success"
                        );
                    }, 500);
                }

            } catch (error) {
                showToast(`${name} 點擊失敗：${error.message}`, "error");
            }

        }, index * 500);
    });

};

document.head.appendChild(scriptTR);
