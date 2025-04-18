// 1. 現在官網沒有jQuery，自己import
if (typeof jQuery === 'undefined') {
  const script = document.createElement('script');
  script.src = "https://code.jquery.com/jquery-3.6.0.min.js";
  script.onload = start;
  document.head.appendChild(script);
} else {
  start();
}

async function start() {
  const baseUrl = "https://chiikawamarket.jp";

  const links = $(".product--root a").map(function () {
    //売り切れ
    console.log($(this).prev("div.product--label-container").find("div.product--label").length)
    if($(this).prev("div.product--label-container").find("div.product--label").length>0) return null;
    
    return {
      url: baseUrl + $(this).attr("href"),
      name: $(this).attr("aria-label") || $(this).find(".product_name").text().trim() || "未命名"
    };
  }).get();

  for (const { url, name } of links) {
    try {
      const html = await $.get(url);
      const metaMatch = html.match(/var meta\s*=\s*({[\s\S]*?});/);
      if (metaMatch && metaMatch[1]) {
        const metaJson = JSON.parse(metaMatch[1]);
        const variantId = metaJson.product?.variants?.[0]?.id;
        if (variantId) {
          await addToCart({ id: variantId, quantity: 1, name });
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

// 2. 加入購物車
async function addToCart(product) {
  const url = "https://chiikawamarket.jp/cart/add.js";
  const headers = {
    "accept": "application/javascript",
    "content-type": "application/json"
  };

  try {
    const response = await fetch(url, {
      method: "POST",
      headers,
      body: JSON.stringify({ items: [{ id: product.id, quantity: product.quantity }] }),
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

// 3. Toast 訊息處理
function showToast(message, type) {
  const toast = document.createElement("small");
  toast.style.cssText = `width:300px;background:#000;color:#fff;padding:5px;border-radius:8px;opacity:0.9;`;
  let icon = "";
  if (type == "success") icon += "✅";
  else if (type == "warning") icon += "⚠️";
  else if (type == "error") icon += "❌";
  toast.innerHTML = icon + " " + message;

  const container = document.getElementById("toast-container") || createToastContainer();
  container.appendChild(toast);
  setTimeout(() => { toast.style.display = "none"; toast.remove(); }, 3000);
}

function createToastContainer() {
  const container = document.createElement("div");
  container.id = "toast-container";
  container.style.cssText = "position:fixed;top:20px;right:20px;z-index:9999;display:flex;flex-direction:column;gap:10px;";
  document.body.appendChild(container);
  return container;
}
