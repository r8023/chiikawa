
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

    showToast(`找到 ${buttons.length} 個收藏商品`, "success");

    buttons.each(function (index) {
        const $btn = $(this);

        // 直接點擊收藏商品按鈕
        setTimeout(() => {
            $btn.trigger("click");
        }, index * 500);
    });

};

document.head.appendChild(scriptTR);
