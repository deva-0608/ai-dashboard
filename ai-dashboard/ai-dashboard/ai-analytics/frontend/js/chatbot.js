const API = "http://localhost:8000";

/* ================================
   READ URL PARAMS
================================ */
const params = new URLSearchParams(window.location.search);
const reportType = params.get("report_type");
const reportId   = params.get("report_id");

if (!reportType || !reportId) {
  alert("Missing report_type or report_id in URL");
}

/* ================================
   CHAT ELEMENTS
================================ */
const input = document.getElementById("chat-input");
const chat  = document.getElementById("chat-messages");

let DATASET = [];   // 🔑 FULL DATAFRAME FROM BACKEND

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
    if (!res.ok) throw new Error("Chat API failed");
    return res.json();
  })
  .then(data => {
    append(data.summary || "No summary returned", "left");

    // 🔑 SAVE FULL DATASET
    DATASET = Array.isArray(data.data) ? data.data : [];

    if (Array.isArray(data.charts)) {
      renderCharts(data.charts);
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
   BUILD ECHARTS OPTION
================================ */
function buildOption(spec, data) {
  const { type, x, y, title } = spec;

  if (!x) return null;

  // Extract column arrays
  const xData = data.map(r => r[x]).filter(v => v !== null);

  const yData = y ? data.map(r => r[y]).filter(v => v !== null) : [];

  const option = {
    title: { text: title || "" },
    tooltip: {}
  };

  switch (type) {
    case "bar":
      option.xAxis = { type: "category", data: xData };
      option.yAxis = { type: "value" };
      option.series = [{ type: "bar", data: yData }];
      break;

    case "line":
      option.tooltip.trigger = "axis";
      option.xAxis = { type: "category", data: xData };
      option.yAxis = { type: "value" };
      option.series = [{ type: "line", data: yData, smooth: true }];
      break;

    case "area":
      option.tooltip.trigger = "axis";
      option.xAxis = { type: "category", data: xData };
      option.yAxis = { type: "value" };
      option.series = [{ type: "line", data: yData, areaStyle: {}, smooth: true }];
      break;

    case "pie":
    case "donut":
      option.series = [{
        type: "pie",
        radius: type === "donut" ? ["40%", "70%"] : "70%",
        data: data.map(r => ({
          name: r[x],
          value: y ? r[y] : 1
        }))
      }];
      break;

    case "scatter":
      option.xAxis = { type: "value" };
      option.yAxis = { type: "value" };
      option.series = [{
        type: "scatter",
        data: data.map(r => [r[x], r[y]])
      }];
      break;

    case "histogram":
      option.xAxis = { type: "category", data: xData };
      option.yAxis = { type: "value" };
      option.series = [{ type: "bar", data: xData }];
      break;

    default:
      return null;
  }

  return option;
}

/* ================================
   RENDER CHARTS
================================ */
function renderCharts(charts) {
  const cards = document.querySelectorAll(".chart-card");

  charts.forEach((c, i) => {
    if (!cards[i] || !c.spec) return;

    const option = buildOption(c.spec, DATASET);
    if (!option) return;

    const chart = echarts.init(cards[i]);
    chart.setOption(option);
  });
}
