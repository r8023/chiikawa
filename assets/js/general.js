const baseURL = location.origin;

// 現在官網沒有jQuery，自己import
if (typeof jQuery === 'undefined') {
  const script = document.createElement('script');
  script.src = "https://code.jquery.com/jquery-3.6.0.min.js";
  script.onload = start;
  document.head.appendChild(script);
} else {
  start();
}

// Toast 訊息處理
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
