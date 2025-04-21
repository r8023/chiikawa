const general = document.createElement("script");
general.src = "https://r8023.github.io/chiikawa/assets/js/general.js";
general.onload = () => {
    // 現在官網沒有jQuery，自己import
    if (typeof jQuery === 'undefined') {
        const script = document.createElement('script');
        script.src = "https://code.jquery.com/jquery-3.6.0.min.js";
        script.onload = start;
        document.head.appendChild(script);
    } else start();

    async function start() {
        const links = $(".product--root a").map(function() {
            //売り切れ
            if ($(this).prev("div.product--label-container").find("div.product--label").length > 0) return null;

            return {
                url: baseURLTR + $(this).attr("href"),
                name: $(this).attr("aria-label") || $(this).find(".product_name").text().trim() || "未命名"
            };
        }).get();

        for (const {
                url,
                name
            }
            of links) {
            try {
                const html = await $.get(url);
                const metaMatch = html.match(/var meta\s*=\s*({[\s\S]*?});/);
                if (metaMatch && metaMatch[1]) {
                    const metaJson = JSON.parse(metaMatch[1]);
                    const variantId = metaJson.product?.variants?.[0]?.id;
                    if (variantId) {
                        await addToCart({
                            id: variantId,
                            quantity: 1,
                            name
                        });
                    } else {
                        showToast(`${name} 找不到 variant_id`, "warning");
                    }
                } else {
                    showToast(`${name} 抓不到 meta JSON`, "error");
                }
            } catch (e) {
                showToast(`${name} 請求錯誤: ${e.message}`, "error");
            }
        }
    }

    // 加入購物車
    async function addToCart(product) {
        const url = baseURLTR + "/cart/add.js";
        const headers = {
            "accept": "application/javascript",
            "content-type": "application/json"
        };

        try {
            const response = await fetch(url, {
                method: "POST",
                headers,
                body: JSON.stringify({
                    items: [{
                        id: product.id,
                        quantity: product.quantity
                    }]
                }),
                credentials: "include"
            });

            if (response.ok) {
                showToast(`${product.name} <br>成功加入 ${product.quantity} 個`, "success");
            } else {
                const errorData = await response.json();
                showToast(`${product.name} <br>加入失敗: ${errorData.message}`, "warning");
            }
        } catch (error) {
            showToast(`${product.name} <br>請求錯誤: ${error.message}`, "error");
        }
    }
};
document.head.appendChild(general);
