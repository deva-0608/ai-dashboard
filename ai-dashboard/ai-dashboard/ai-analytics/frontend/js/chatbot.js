
const API = "http://localhost:8000";

/* ================================
   READ URL PARAMS (CORRECT)
================================ */
const params = new URLSearchParams(window.location.search);
const reportType = params.get("report_type");   // custom-report
const reportId   = params.get("report_id");     // 33

if (!reportType || !reportId) {
  alert("Missing report_type or report_id in URL");
}

/* ================================
   CHAT ELEMENTS
================================ */
const input = document.getElementById("chat-input");
const chat  = document.getElementById("chat-messages");

input.addEventListener("keypress", e => {
  if (e.key === "Enter") send();
});

/* ================================
   SEND MESSAGE
================================ */
function send() {
  const text = input.value.trim();
  if (!text) return;

  append(text, "right");
  input.value = "";

  fetch(`${API}/reports/design/${reportType}/detail/${reportId}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ prompt: text })
  })
  .then(res => {
    if (!res.ok) {
      throw new Error("Chat API failed");
    }
    return res.json();
  })
  .then(data => {
    append(data.summary || "No summary returned", "left");

    if (Array.isArray(data.charts)) {
      renderCharts(data.charts);
    } else {
      console.warn("No charts returned:", data);
    }
  })
  .catch(err => {
    console.error(err);
    append("Error processing request", "left");
  });
}

/* ================================
   APPEND CHAT MESSAGE
================================ */
function append(msg, side) {
  const div = document.createElement("div");
  div.className = side;
  div.innerText = msg;
  chat.appendChild(div);
  chat.scrollTop = chat.scrollHeight;
}

/* ================================
   RENDER CHARTS (SAFE)
================================ */
function renderCharts(charts) {
  if (!Array.isArray(charts) || charts.length === 0) return;

  const cards = document.querySelectorAll(".chart-card");

  charts.forEach((c, i) => {
    if (!cards[i] || !c.option) return;

    const chart = echarts.init(cards[i]);
    chart.setOption(c.option);
  });
}
