// ─────────────────────────────────────────────
// CONFIGURATION
// ─────────────────────────────────────────────

// TODO: Update this URL when your FastAPI server is running
const API_BASE_URL = "http://127.0.0.1:8000";

const ENDPOINTS = {
  health:  `${API_BASE_URL}/health`,
  metrics: `${API_BASE_URL}/metrics`,
};

// ─────────────────────────────────────────────
// STATE
// ─────────────────────────────────────────────

let autoRefreshTimer = null;
let charts = {};

// ─────────────────────────────────────────────
// API CALLS
// ─────────────────────────────────────────────

async function checkHealth() {
  const dot   = document.getElementById("status-dot");
  const label = document.getElementById("api-status");
  try {
    const res = await fetch(ENDPOINTS.health, { signal: AbortSignal.timeout(3000) });
    if (res.ok) {
      dot.className   = "online";
      label.textContent = "API Online";
    } else {
      dot.className   = "offline";
      label.textContent = "API Error";
    }
  } catch {
    dot.className   = "offline";
    label.textContent = "API Offline";
  }
}

async function fetchMetrics() {
  const res = await fetch(ENDPOINTS.metrics, { signal: AbortSignal.timeout(5000) });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return await res.json();
}

// ─────────────────────────────────────────────
// MAIN LOAD
// ─────────────────────────────────────────────

async function loadData() {
  await checkHealth();
  try {
    const data = await fetchMetrics();

    if (!data || data.length === 0) {
      showEmptyState();
      return;
    }

    // Sort ascending by timestamp for charts
    const sorted = [...data].sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));

    updateKPIs(data, sorted);
    updateCharts(sorted);
    updateTable(data.slice(0, 50));

    document.getElementById("last-updated").textContent =
      `Last updated: ${new Date().toLocaleTimeString()}`;

  } catch (err) {
    console.error("Failed to load metrics:", err);
    showErrorState(err.message);
  }
}

// ─────────────────────────────────────────────
// KPI CARDS
// ─────────────────────────────────────────────

function updateKPIs(data, sorted) {
  const total       = data.length;
  const anomalies   = data.filter(r => r.anomaly_detected).length;
  const anomalyPct  = total > 0 ? ((anomalies / total) * 100).toFixed(1) : 0;
  const avgErrorRate = (data.reduce((s, r) => s + r.error_rate, 0) / total * 100).toFixed(2);
  const avgRequests  = Math.round(data.reduce((s, r) => s + r.total_requests, 0) / total);
  const last         = sorted[sorted.length - 1];

  document.getElementById("kpi-total-val").textContent       = total.toLocaleString();
  document.getElementById("kpi-anomalies-val").textContent   = anomalies.toLocaleString();
  document.getElementById("kpi-anomalies-pct").textContent   = `${anomalyPct}% of total runs`;
  document.getElementById("kpi-error-rate-val").textContent  = `${avgErrorRate}%`;
  document.getElementById("kpi-requests-val").textContent    = avgRequests.toLocaleString();

  // Last run status card
  if (last) {
    const lastCard = document.getElementById("kpi-last-run");
    document.getElementById("kpi-last-run-val").textContent  = last.anomaly_detected ? "ANOMALY" : "Normal";
    document.getElementById("kpi-last-run-time").textContent = formatTimestamp(last.timestamp);
    lastCard.className = `kpi-card ${last.anomaly_detected ? "anomaly" : "healthy"}`;
  }

  // Anomalies card color
  document.getElementById("kpi-anomalies").className =
    `kpi-card ${anomalies > 0 ? "anomaly" : "healthy"}`;
}

// ─────────────────────────────────────────────
// CHARTS
// ─────────────────────────────────────────────

const CHART_DEFAULTS = {
  responsive: true,
  maintainAspectRatio: true,
  plugins: { legend: { display: false } },
  scales: {
    x: {
      ticks: { color: "#8b949e", maxTicksLimit: 8, maxRotation: 0 },
      grid:  { color: "rgba(48,54,61,0.5)" },
    },
    y: {
      ticks: { color: "#8b949e" },
      grid:  { color: "rgba(48,54,61,0.5)" },
    },
  },
};

function getTimeLabels(sorted) {
  return sorted.map(r => {
    const d = new Date(r.timestamp);
    return `${d.getHours().toString().padStart(2, "0")}:${d.getMinutes().toString().padStart(2, "0")}`;
  });
}

function destroyChart(id) {
  if (charts[id]) { charts[id].destroy(); delete charts[id]; }
}

function updateCharts(sorted) {
  const labels = getTimeLabels(sorted);

  // ── Error Rate ──
  destroyChart("error-rate");
  charts["error-rate"] = new Chart(document.getElementById("chart-error-rate"), {
    type: "line",
    data: {
      labels,
      datasets: [{
        data: sorted.map(r => (r.error_rate * 100).toFixed(2)),
        borderColor: "#f85149",
        backgroundColor: "rgba(248,81,73,0.1)",
        fill: true,
        tension: 0.3,
        pointBackgroundColor: sorted.map(r => r.anomaly_detected ? "#f85149" : "#58a6ff"),
        pointRadius: sorted.map(r => r.anomaly_detected ? 6 : 3),
      }],
    },
    options: {
      ...CHART_DEFAULTS,
      scales: {
        ...CHART_DEFAULTS.scales,
        y: {
          ...CHART_DEFAULTS.scales.y,
          ticks: { ...CHART_DEFAULTS.scales.y.ticks, callback: v => v + "%" },
        },
      },
    },
  });

  // ── Total Requests ──
  destroyChart("requests");
  charts["requests"] = new Chart(document.getElementById("chart-requests"), {
    type: "bar",
    data: {
      labels,
      datasets: [{
        data: sorted.map(r => r.total_requests),
        backgroundColor: sorted.map(r =>
          r.anomaly_detected ? "rgba(248,81,73,0.7)" : "rgba(88,166,255,0.5)"
        ),
        borderColor: sorted.map(r => r.anomaly_detected ? "#f85149" : "#58a6ff"),
        borderWidth: 1,
      }],
    },
    options: CHART_DEFAULTS,
  });

  // ── Avg Bytes KB ──
  destroyChart("bytes");
  charts["bytes"] = new Chart(document.getElementById("chart-bytes"), {
    type: "line",
    data: {
      labels,
      datasets: [
        {
          label: "avg_bytes_kb",
          data: sorted.map(r => r.avg_bytes_kb.toFixed(2)),
          borderColor: "#3fb950",
          backgroundColor: "rgba(63,185,80,0.1)",
          fill: true,
          tension: 0.3,
          pointRadius: 2,
        },
        {
          label: "std_bytes_kb",
          data: sorted.map(r => r.std_bytes_kb.toFixed(2)),
          borderColor: "#d29922",
          backgroundColor: "transparent",
          borderDash: [4, 4],
          tension: 0.3,
          pointRadius: 0,
        },
      ],
    },
    options: {
      ...CHART_DEFAULTS,
      plugins: {
        legend: {
          display: true,
          labels: { color: "#8b949e", boxWidth: 12 },
        },
      },
    },
  });

  // ── Anomaly Timeline ──
  destroyChart("anomalies");
  charts["anomalies"] = new Chart(document.getElementById("chart-anomalies"), {
    type: "bar",
    data: {
      labels,
      datasets: [{
        data: sorted.map(r => r.anomaly_detected ? 1 : 0),
        backgroundColor: sorted.map(r =>
          r.anomaly_detected ? "rgba(248,81,73,0.8)" : "rgba(63,185,80,0.4)"
        ),
        borderWidth: 0,
      }],
    },
    options: {
      ...CHART_DEFAULTS,
      scales: {
        ...CHART_DEFAULTS.scales,
        y: {
          ...CHART_DEFAULTS.scales.y,
          max: 1,
          ticks: {
            ...CHART_DEFAULTS.scales.y.ticks,
            stepSize: 1,
            callback: v => v === 1 ? "Anomaly" : "Normal",
          },
        },
      },
    },
  });
}

// ─────────────────────────────────────────────
// TABLE
// ─────────────────────────────────────────────

function updateTable(data) {
  const tbody = document.getElementById("table-body");
  if (!data.length) { showEmptyState(); return; }

  tbody.innerHTML = data.map(r => `
    <tr>
      <td>${r.id}</td>
      <td>${formatTimestamp(r.timestamp)}</td>
      <td>${r.total_requests.toLocaleString()}</td>
      <td>${(r.error_rate * 100).toFixed(2)}%</td>
      <td>${r.avg_bytes_kb.toFixed(2)}</td>
      <td>${r.std_bytes_kb.toFixed(2)}</td>
      <td>${(r.empty_response_rate * 100).toFixed(2)}%</td>
      <td>${r.unique_endpoints}</td>
      <td>
        <span class="badge ${r.anomaly_detected ? 'anomaly' : 'normal'}">
          ${r.anomaly_detected ? '⚠ Anomaly' : '✓ Normal'}
        </span>
      </td>
    </tr>
  `).join("");
}

// ─────────────────────────────────────────────
// AUTO REFRESH
// ─────────────────────────────────────────────

function toggleAutoRefresh() {
  const btn   = document.getElementById("auto-refresh-label").parentElement;
  const label = document.getElementById("auto-refresh-label");

  if (autoRefreshTimer) {
    clearInterval(autoRefreshTimer);
    autoRefreshTimer = null;
    label.textContent    = "▶ Auto Refresh (30s)";
    btn.style.background = "";
    btn.style.borderColor = "";
    btn.style.color      = "";
  } else {
    autoRefreshTimer = setInterval(loadData, 30000);
    label.textContent    = "⏹ Stop Auto Refresh";
    btn.style.background = "rgba(63,185,80,0.15)";
    btn.style.borderColor = "#3fb950";
    btn.style.color      = "#3fb950";
  }
}

// ─────────────────────────────────────────────
// HELPERS
// ─────────────────────────────────────────────

function formatTimestamp(ts) {
  if (!ts) return "—";
  const d = new Date(ts);
  return isNaN(d) ? ts : d.toLocaleString();
}

function showEmptyState() {
  document.getElementById("table-body").innerHTML = `
    <tr>
      <td colspan="9">
        <div class="empty-state">
          <strong>No data yet</strong>
          <p>Run the pipeline at least once to see data here.</p>
        </div>
      </td>
    </tr>`;
}

function showErrorState(msg) {
  document.getElementById("table-body").innerHTML = `
    <tr>
      <td colspan="9">
        <div class="empty-state">
          <strong>Failed to load data</strong>
          <p>${msg}</p>
          <p style="margin-top:8px;font-size:12px;">
            Make sure the FastAPI server is running on <code>${API_BASE_URL}</code>
          </p>
        </div>
      </td>
    </tr>`;
}

// ─────────────────────────────────────────────
// PIPELINE & TRAIN ACTIONS
// ─────────────────────────────────────────────

async function runPipeline() {
  const btn   = document.getElementById("btn-run-pipeline");
  const label = document.getElementById("btn-run-pipeline-label");

  btn.disabled    = true;
  label.textContent = "⏳ Running...";

  try {
    const res = await fetch(`${API_BASE_URL}/run-pipeline`, {
      method: "POST",
      signal: AbortSignal.timeout(60000),
    });

    if (res.ok) {
      const data = await res.json();
      const isAnomaly = data.anomaly_detected;
      showToast(
        isAnomaly
          ? `⚠ Pipeline ran — ANOMALY detected! (${data.message || ""})`
          : `✓ Pipeline ran successfully — No anomaly detected.`,
        isAnomaly ? "error" : "success"
      );
      // Reload data to show the new row
      await loadData();
    } else {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      showToast(`✗ Pipeline failed: ${err.detail || res.statusText}`, "error");
    }
  } catch (err) {
    showToast(`✗ Could not reach API: ${err.message}`, "error");
  } finally {
    btn.disabled    = false;
    label.textContent = "▶ Run Pipeline";
  }
}

async function trainModel() {
  const btn   = document.getElementById("btn-train-model");
  const label = document.getElementById("btn-train-model-label");

  btn.disabled    = true;
  label.textContent = "⏳ Training...";
  showToast("⚙ Training model... this may take a few seconds.", "info");

  try {
    const res = await fetch(`${API_BASE_URL}/train-model`, {
      method: "POST",
      signal: AbortSignal.timeout(120000),
    });

    if (res.ok) {
      const data = await res.json();
      showToast(`✓ Model trained successfully! ${data.message || ""}`, "success");
    } else {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      showToast(`✗ Training failed: ${err.detail || res.statusText}`, "error");
    }
  } catch (err) {
    showToast(`✗ Could not reach API: ${err.message}`, "error");
  } finally {
    btn.disabled    = false;
    label.textContent = "⚙ Train / Retrain Model";
  }
}

// ─────────────────────────────────────────────
// TOAST NOTIFICATION
// ─────────────────────────────────────────────

let toastTimer = null;

function showToast(message, type = "info", duration = 5000) {
  const toast = document.getElementById("toast");
  toast.textContent  = message;
  toast.className    = `toast ${type}`;

  if (toastTimer) clearTimeout(toastTimer);
  toastTimer = setTimeout(() => {
    toast.className = "toast hidden";
  }, duration);
}

// ─────────────────────────────────────────────
// INIT
// ─────────────────────────────────────────────
loadData();
