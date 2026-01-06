// const API = "http://localhost:8000";

// /* ================================
//    READ URL PARAMS
// ================================ */
// const params = new URLSearchParams(window.location.search);
// const reportType = params.get("report_type");
// const reportId   = params.get("report_id");

// if (!reportType || !reportId) {
//   alert("Missing report_type or report_id in URL");
// }

// /* ================================
//    CHAT ELEMENTS
// ================================ */
// const input = document.getElementById("chat-input");
// const chat  = document.getElementById("chat-messages");

// let DATASET = [];   // 🔑 FULL DATAFRAME FROM BACKEND

// input.addEventListener("keypress", e => {
//   if (e.key === "Enter") send();
// });

// /* ================================
//    SEND MESSAGE
// ================================ */
// function send() {
//   const text = input.value.trim();
//   if (!text) return;

//   append(text, "right");
//   input.value = "";

//   fetch(`${API}/reports/design/${reportType}/detail/${reportId}/chat`, {
//     method: "POST",
//     headers: { "Content-Type": "application/json" },
//     body: JSON.stringify({ prompt: text })
//   })
//   .then(res => {
//     if (!res.ok) throw new Error("Chat API failed");
//     return res.json();
//   })
//   .then(data => {
//     append(data.summary || "No summary returned", "left");

//     // 🔑 SAVE FULL DATASET
//     DATASET = Array.isArray(data.data) ? data.data : [];

//     if (Array.isArray(data.charts)) {
//       renderCharts(data.charts);
//     }
//   })
//   .catch(err => {
//     console.error(err);
//     append("Error processing request", "left");
//   });
// }

// /* ================================
//    APPEND CHAT MESSAGE
// ================================ */
// function append(msg, sender) {
//   const div = document.createElement("div");
//   div.classList.add("msg");

//   if (sender === "user") {
//     div.classList.add("user");
//   } else {
//     div.classList.add("ai");
//   }

//   div.innerText = msg;
//   chat.appendChild(div);
//   chat.scrollTop = chat.scrollHeight;
// }


// /* ================================
//    BUILD ECHARTS OPTION
// ================================ */
// function buildOption(spec, data) {
//   const { type, x, y, title } = spec;
//   if (!x) return null;

//   const option = {
//     title: { text: title || "" },
//     tooltip: {}
//   };

//   /* ============================
//      🔑 COUNT PLOTS (y == null)
//   ============================ */
//   if (y === null) {
//     const { labels, values } = buildCounts(data, x);

//     if (type === "bar") {
//       option.xAxis = { type: "category", data: labels };
//       option.yAxis = { type: "value" };
//       option.series = [{ type: "bar", data: values }];
//       return option;
//     }

//     if (type === "pie" || type === "donut") {
//       option.series = [{
//         type: "pie",
//         radius: type === "donut" ? ["40%", "70%"] : "70%",
//         data: labels.map((l, i) => ({
//           name: l,
//           value: values[i]
//         }))
//       }];
//       return option;
//     }
//   }

//   /* ============================
//      NORMAL X–Y CHARTS
//   ============================ */
//   const xData = data.map(r => r[x]).filter(v => v !== null);
//   const yData = y ? data.map(r => r[y]).filter(v => v !== null) : [];

//   switch (type) {
//     case "bar":
//       option.xAxis = { type: "category", data: xData };
//       option.yAxis = { type: "value" };
//       option.series = [{ type: "bar", data: yData }];
//       break;

//     case "line":
//       option.tooltip.trigger = "axis";
//       option.xAxis = { type: "category", data: xData };
//       option.yAxis = { type: "value" };
//       option.series = [{ type: "line", data: yData, smooth: true }];
//       break;

//     case "area":
//       option.tooltip.trigger = "axis";
//       option.xAxis = { type: "category", data: xData };
//       option.yAxis = { type: "value" };
//       option.series = [{ type: "line", data: yData, areaStyle: {}, smooth: true }];
//       break;

//     case "scatter":
//       option.xAxis = { type: "value" };
//       option.yAxis = { type: "value" };
//       option.series = [{
//         type: "scatter",
//         data: data.map(r => [r[x], r[y]])
//       }];
//       break;

//     case "histogram":
//       option.xAxis = { type: "category", data: xData };
//       option.yAxis = { type: "value" };
//       option.series = [{ type: "bar", data: xData }];
//       break;

//     case "pie":
//       option.series = [{
//         type: "pie",
//         radius: "70%",
//         data: data.map(r => ({
//           name: r[x],
//           value: r[y]
//         }))
//       }];
//       break;

//     default:
//       return null;
//   }

//   return option;
// }

// /* ================================
//    RENDER CHARTS
// ================================ */
// function renderCharts(charts) {
//   const cards = document.querySelectorAll(".chart-card");

//   charts.forEach((c, i) => {
//     if (!cards[i]) return;
//     const chart = echarts.init(cards[i]);
//     chart.setOption(c.option);
//   });
// }

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

const chartsContainer = document.getElementById("charts-container");
const kpiTable = document.getElementById("kpi-table");

let DATASET = [];

input.addEventListener("keypress", e => {
  if (e.key === "Enter") send();
});

/* ================================
   SEND MESSAGE
================================ */
function send() {
  const text = input.value.trim();
  if (!text) return;

  append(text, "user");
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
    append(data.summary || "No summary returned", "ai");

    DATASET = Array.isArray(data.data) ? data.data : [];

    renderKPIs(data.kpis || []);
    renderCharts(data.charts || []);
  })
  .catch(err => {
    console.error(err);
    append("Error processing request", "ai");
  });
}

/* ================================
   CHAT BUBBLES
================================ */
function append(msg, sender) {
  const div = document.createElement("div");
  div.classList.add("msg", sender === "user" ? "user" : "ai");
  div.innerText = msg;
  chat.appendChild(div);
  chat.scrollTop = chat.scrollHeight;
}

/* ================================
   KPI RENDERING
================================ */
function renderKPIs(kpis) {
  kpiTable.innerHTML = "";

  if (!kpis.length) {
    kpiTable.innerHTML = `
      <tr>
        <td colspan="2" style="text-align:center;color:#8a7f55;">
          No KPIs generated
        </td>
      </tr>
    `;
    return;
  }

  kpis.forEach(kpi => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${kpi.name}</td>
      <td><strong>${kpi.value}</strong></td>
    `;
    kpiTable.appendChild(tr);
  });
}

/* ================================
   CHART RENDERING
================================ */
function renderCharts(charts) {
  chartsContainer.innerHTML = "";

  if (!charts.length) {
    chartsContainer.innerHTML = `
      <div style="color:#8a7f55;padding:16px;">
        No charts generated
      </div>
    `;
    return;
  }

  charts.forEach(chart => {
    const card = document.createElement("div");
    card.className = "chart-card";

    const inner = document.createElement("div");
    inner.className = "chart-inner";

    card.appendChild(inner);
    chartsContainer.appendChild(card);

    const instance = echarts.init(inner);
    instance.setOption(chart.option);
  });
}
