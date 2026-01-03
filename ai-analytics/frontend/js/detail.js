const pathParts = window.location.pathname.split("/");
const reportType = pathParts[3];
const reportId = pathParts[5];

function toggleChat() {
  document.getElementById("chat-panel").classList.toggle("hidden");
}

async function sendPrompt() {
  const prompt = document.getElementById("prompt").value;

  const res = await fetch(
    `/api/reports/${reportType}/detail/${reportId}/chat`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ prompt })
    }
  );

  const result = await res.json();
  renderDashboard(result);
}

function renderDashboard(result) {
  const dash = document.getElementById("dashboard");
  dash.innerHTML = "";

  result.charts.forEach(c => {
    const div = document.createElement("div");
    div.style.height = "300px";
    dash.appendChild(div);

    const chart = echarts.init(div);
    chart.setOption({
      title: { text: c.title },
      tooltip: {},
      xAxis: { type: "category", data: result.data[c.id].map(d => d[c.x]) },
      yAxis: {},
      series: [{ type: c.type, data: result.data[c.id].map(d => d[c.y]) }]
    });
  });

  document.getElementById("insights").innerText = result.summary;
}
