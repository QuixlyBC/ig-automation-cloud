const addBtn = document.getElementById("addBtn");
const reelUrl = document.getElementById("reelUrl");
const addStatus = document.getElementById("addStatus");
const queueList = document.getElementById("queueList");
const emptyMsg = document.getElementById("emptyMsg");
const customDescription = document.getElementById("customDescription");
const charCount = document.getElementById("charCount");

// Stats
const totalCount = document.getElementById("totalCount");
const postedCount = document.getElementById("postedCount");
const pendingCount = document.getElementById("pendingCount");
const failedCount = document.getElementById("failedCount");

// Character counter for description
if (customDescription) {
  customDescription.addEventListener("input", () => {
    charCount.textContent = customDescription.value.length + " characters";
  });
}

async function postJSON(url, body) {
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body || {}),
  });
  return res.json();
}

addBtn.addEventListener("click", async () => {
  const url = reelUrl.value.trim();
  if (!url) {
    addStatus.textContent = "Paste a URL first.";
    return;
  }
  
  const desc = customDescription ? customDescription.value.trim() : "";
  
  addBtn.disabled = true;
  addStatus.textContent = "Adding to queue...";
  
  try {
    const result = await postJSON("/api/add", { url, description: desc || null });
    if (result.ok) {
      addStatus.textContent = "✓ Added to queue";
      reelUrl.value = "";
      if (customDescription) customDescription.value = "";
      if (charCount) charCount.textContent = "0 characters";
      refreshQueue();
    } else {
      addStatus.textContent = "Error: " + result.error;
    }
  } catch (e) {
    addStatus.textContent = "Error: " + e.message;
  }
  
  addBtn.disabled = false;
});

async function refreshQueue() {
  try {
    const res = await fetch("/api/queue");
    const data = await res.json();
    const items = data.items || [];
    const stats = data.stats || {};
    
    // Update stats
    totalCount.textContent = stats.total || 0;
    postedCount.textContent = stats.posted || 0;
    pendingCount.textContent = stats.pending || 0;
    failedCount.textContent = stats.failed || 0;
    
    // Update queue list
    queueList.innerHTML = "";
    if (items.length === 0) {
      emptyMsg.style.display = "block";
      return;
    }
    emptyMsg.style.display = "none";
    
    items.forEach(item => {
      const div = document.createElement("div");
      div.className = "queue-item";
      
      const statusClass = `status-${item.status}`;
      const createdDate = new Date(item.created_at).toLocaleDateString();
      
      let content = `
        <div class="queue-item-info">
          <span class="queue-item-status ${statusClass}">${item.status}</span>
          <a href="${item.url}" target="_blank" class="queue-item-url">${item.url}</a>
          <div class="queue-item-time">${createdDate}</div>
      `;
      
      if (item.error) {
        content += `<div style="color: #f44336; font-size: 0.8rem; margin-top: 4px;">Error: ${item.error}</div>`;
      }
      
      if (item.posted_url) {
        content += `<a href="${item.posted_url}" target="_blank" class="queue-item-link">View posted reel →</a>`;
      }
      
      content += `</div>`;
      content += `<div class="queue-item-actions"><button onclick="deleteItem(${item.id})">Remove</button></div>`;
      
      div.innerHTML = content;
      queueList.appendChild(div);
    });
  } catch (e) {
    console.error("Error refreshing queue:", e);
  }
}

async function deleteItem(itemId) {
  if (!confirm("Remove this item?")) return;
  
  try {
    const res = await fetch(`/api/delete/${itemId}`, { method: "DELETE" });
    const data = await res.json();
    if (data.ok) {
      refreshQueue();
    }
  } catch (e) {
    console.error("Error deleting:", e);
  }
}

// Initial load and refresh every 5 seconds
refreshQueue();
setInterval(refreshQueue, 5000);

// Allow Enter key to submit
reelUrl.addEventListener("keypress", (e) => {
  if (e.key === "Enter") addBtn.click();
});
