if (!document.querySelector('script[src="https://r8023.github.io/chiikawa/assets/js/general.js"]')) {
	const general = document.createElement("script");
	general.src = "https://r8023.github.io/chiikawa/assets/js/general.js";
	general.onload = () => {
		if (typeof jQuery === 'undefined') {
			const script = document.createElement('script');
			script.src = "https://code.jquery.com/jquery-3.6.0.min.js";
			script.onload = start;
			document.head.appendChild(script);
		} else start();
	};
	document.head.appendChild(general);
} else {
	console.log("general.js 已經載入");
	if (typeof jQuery === 'undefined') {
		const script = document.createElement('script');
		script.src = "https://code.jquery.com/jquery-3.6.0.min.js";
		script.onload = start;
		document.head.appendChild(script);
	} else start();
}

async function start() {
	const productData = [
	  { id: "43891553108209", quantity: 1, name: "辣咖哩兔兔" },
	  { id: "43891553042673", quantity: 1, name: "辣咖哩小八" },
	  { id: "43891553009905", quantity: 1, name: "辣咖哩吉伊" },
	  { id: "42919073972465", quantity: 1, name: "雞腿哥布林" },
	  { id: "45624328290545", quantity: 1, name: "哭哭哥布林" },
	  { id: "43764095484145", quantity: 1, name: "惡兔" },
	  { id: "43764095516913", quantity: 1, name: "惡栗子" },
	  { id: "43701908766961", quantity: 1, name: "墮天使小八" },
	  { id: "43701908799729", quantity: 1, name: "惡魔兔兔" },
	  { id: "43701908832497", quantity: 1, name: "惡魔栗子" },
	  { id: "43701908963569", quantity: 1, name: "天使師傅" },
	  //{ id: "49883693121857", quantity: 1, name: "地瓜吉伊" },
	  //{ id: "49883693154625", quantity: 1, name: "地瓜小八" },
	  //{ id: "49883693220161", quantity: 1, name: "地瓜兔兔" }
	];

	async function addToCart(products, retryCount = 2) {
	  const url = baseURLTR+"/cart/add.js";
	  const headers = {
	    "accept": "application/javascript",
	    "content-type": "application/json"
	  };

	  for (const product of products) {
	    let retries = 0;
	    while (retries <= retryCount) {
	      try {
	        const response = await fetch(url, {
	          method: "POST",
	          headers,
	          body: JSON.stringify({ items: [{ id: product.id, quantity: product.quantity }] }),
	          credentials: "include"
	        });

	        if (response.ok) {
	          showToast(`商品 ${product.name} (${product.quantity} 個) 加入成功`, "success");
	          break; // 成功後結束重試
	        } else {
	          const errorData = await response.json();
	          showToast(`商品 ${product.name} 加入失敗: ${errorData.message} (重試 ${retries}/${retryCount})`, "warning");
	        }
	      } catch (error) {
	        showToast(`商品 ${product.name} 請求錯誤: ${error.message} (重試 ${retries}/${retryCount})`, "error");
	      }

	      retries++;
	      if (retries <= retryCount) {
	        await new Promise(resolve => setTimeout(resolve, 2000)); // 2 秒後重試
	      }
	    }
	  }
	}

	// 依序加入購物車
	addToCart(productData, 1);
}
