// ------------------------------
// FloodSystem Frontend JS
// ------------------------------

const API_BASE = "https://disaster-metrics-backend.onrender.com";
let map;
let mapMarker = null;
let gaugeChart = null;
let alertAudio = null;

// ---------- INIT ----------
window.addEventListener("DOMContentLoaded", () => {
  alertAudio = document.getElementById("alertSound");

  initMap();
  initGauge();
  initGraphs();
  initChatAssistant();

  // Weather button
  document.getElementById("btn-weather").addEventListener("click", () => {
    const city = document.getElementById("weather-city").value || "Indore";
    fetchWeather(city);
  });

  // Prediction button
  document.getElementById("btn-predict").addEventListener("click", runPrediction);

  // Slider labels
  ["monsoon", "urban", "dams"].forEach((name) => {
    const slider = document.getElementById(`slider-${name}`);
    const label = document.getElementById(`val-${name}`);
    const update = () => (label.textContent = slider.value);
    slider.addEventListener("input", update);
    update();
  });

  // Initial weather
  document.getElementById("weather-city").value = "Indore";
  fetchWeather("Indore");
});

// ---------- WEATHER ----------
async function fetchWeather(city) {
  try {
    const res = await fetch(`${API_BASE}/api/weather?q=${encodeURIComponent(city)}`);
    const data = await res.json();

    if (!res.ok || data.error) {
      alert("Error fetching weather");
      console.error(data.error || data);
      return;
    }

    const temp = data.main?.temp;
    const hum = data.main?.humidity;
    const desc = data.weather && data.weather[0]?.description;

    document.getElementById("weather-text").textContent =
      `${temp} °C — Humidity ${hum}% — ${desc}`;

    const lat = data.coord?.lat;
    const lon = data.coord?.lon;
    if (lat && lon) {
      updateMap(lat, lon, city, temp, hum, desc);
    }
  } catch (e) {
    console.error(e);
    alert("Error fetching weather");
  }
}

// ---------- PREDICTION ----------
async function runPrediction() {
  const payload = {
    monsoon: Number(document.getElementById("slider-monsoon").value),
    urban: Number(document.getElementById("slider-urban").value),
    dams: Number(document.getElementById("slider-dams").value),
  };

  try {
    const res = await fetch(`${API_BASE}/api/predict`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    const data = await res.json();

    if (!res.ok || data.error || data.status !== "ok") {
      alert(`Prediction error: ${data.error || "Unknown error"}`);
      console.error(data);
      return;
    }

    const result = data.result || data.flood_risk || {};
    const prob = typeof result.probability === "number" ? result.probability : 0;
    const risk = result.risk_level || "Unknown";

    updateFloodAlert(prob, risk);

    if (risk === "High") {
      notifyFlood("High flood risk detected!");
    }

  } catch (e) {
    console.error(e);
    alert("Prediction error!");
  }
}

// ---------- GAUGE / ALERT ----------
function initGauge() {
  const ctx = document.getElementById("floodGauge").getContext("2d");

  gaugeChart = new Chart(ctx, {
    type: "doughnut",
    data: {
      labels: ["Flood probability", "Safe"],
      datasets: [
        {
          data: [0, 1],
          backgroundColor: ["#ff4b81", "#1f2933"],
          borderWidth: 0,
        },
      ],
    },
    options: {
      cutout: "70%",
      plugins: {
        legend: { display: false },
        tooltip: { enabled: false },
      },
    },
  });
}

function updateFloodAlert(prob, risk) {
  const pct = Math.round(prob * 100);

  if (gaugeChart) {
    gaugeChart.data.datasets[0].data = [prob, 1 - prob];
    gaugeChart.update();
  }

  const status = document.getElementById("alert-status");
  const detail = document.getElementById("alert-detail");

  status.textContent = `Flood Risk: ${risk} (${pct}%)`;

  if (risk === "Low") {
    detail.textContent = "Low risk. Conditions are generally safe.";
  } else if (risk === "Moderate") {
    detail.textContent = "Moderate risk. Stay alert and monitor updates.";
  } else if (risk === "High") {
    detail.textContent = "High risk! Take precautions and monitor warnings.";
  } else {
    detail.textContent = "Prediction available, but risk level unknown.";
  }
}

function notifyFlood(message) {
  if (alertAudio) {
    alertAudio.currentTime = 0;
    alertAudio.play().catch(() => {});
  }
  console.log("Flood alert:", message);
}

// ---------- MAP ----------
function initMap() {
  map = L.map("map").setView([22.9734, 78.6569], 5); // India center

  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution: "&copy; OpenStreetMap contributors",
  }).addTo(map);
}

function updateMap(lat, lon, city, temp, hum, desc) {
  if (!map) return;

  if (mapMarker) {
    map.removeLayer(mapMarker);
  }

  map.setView([lat, lon], 9);

  mapMarker = L.marker([lat, lon]).addTo(map);
  mapMarker.bindPopup(
    `<b>${city}</b><br/>🌡 Temp: ${temp}°C<br/>💧 Humidity: ${hum}%<br/>${desc}`
  );
}

// ---------- GRAPHS ----------
async function initGraphs() {
  try {
    const res = await fetch(`${API_BASE}/api/graphs`);
    const data = await res.json();

    if (!res.ok || data.error) {
      console.error("Error loading graphs", data.error);
      return;
    }

    buildScatter("graph-monsoon", data.monsoon, "Monsoon vs FloodProb", "#3b82f6", "Monsoon Intensity");
    buildScatter("graph-urban", data.urban, "Urbanization vs FloodProb", "#ec4899", "Urbanization Level");
    buildScatter("graph-dams", data.dams, "DamsQuality vs FloodProb", "#22c55e", "Dams Quality");
  } catch (e) {
    console.error("Graph init error", e);
  }
}

function buildScatter(canvasId, xy, label, color, xLabel) {
  const canvas = document.getElementById(canvasId);
  if (!canvas) return;

  const ctx = canvas.getContext("2d");
  const points = (xy.x || []).map((xVal, i) => ({
    x: xVal,
    y: xy.y[i],
  }));

  new Chart(ctx, {
    type: "scatter",
    data: {
      datasets: [
        {
          label,
          data: points,
          backgroundColor: color,
          borderColor: color,
          pointBackgroundColor: color,
          pointBorderColor: color,
          pointRadius: 2,
          pointHoverRadius: 3,
          showLine: false,
        },
      ],
    },
    options: {
      plugins: { legend: { display: false } },
      scales: {
        x: {
          title: { display: true, text: xLabel },
          grid: { color: "#1f2933" },
          ticks: { color: "#e5e7eb" },
        },
        y: {
          title: { display: true, text: "Flood Probability" },
          min: 0,
          max: 1,
          grid: { color: "#1f2933" },
          ticks: { color: "#e5e7eb" },
        },
      },
    },
  });
}

// ---------- FLOATING CHAT ASSISTANT ----------
function initChatAssistant() {
  const chatBtn = document.getElementById("chat-button");
  const chatPopup = document.getElementById("chat-popup");
  const chatClose = document.getElementById("chat-close");
  const chatSend = document.getElementById("chat-send");
  const chatInput = document.getElementById("chat-input");
  const chatMessages = document.getElementById("chat-messages");

  if (!chatBtn || !chatPopup || !chatClose || !chatSend || !chatInput || !chatMessages) {
    console.warn("Chat elements not found in DOM.");
    return;
  }

  chatBtn.addEventListener("click", () => {
    chatPopup.style.display = "flex";
  });

  chatClose.addEventListener("click", () => {
    chatPopup.style.display = "none";
  });

  chatSend.addEventListener("click", () => sendChatMessage(chatInput, chatMessages));
  chatInput.addEventListener("keypress", (e) => {
    if (e.key === "Enter") sendChatMessage(chatInput, chatMessages);
  });
}

function sendChatMessage(chatInput, chatMessages) {
  const text = chatInput.value.trim();
  if (!text) return;

  addChatMessage(text, "user", chatMessages);
  chatInput.value = "";

  setTimeout(() => {
    const reply = getBotReply(text);
    addChatMessage(reply, "bot", chatMessages);
  }, 500);
}

function addChatMessage(text, sender, chatMessages) {
  const div = document.createElement("div");
  div.className = `chat-msg chat-${sender}`;
  div.textContent = text;
  chatMessages.appendChild(div);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Simple rule-based bot
function getBotReply(q) {
  const text = q.toLowerCase();

  if (text.includes("evacuate") || text.includes("evacuation") || text.includes("escape")) {
    return "During evacuation: move to higher ground, avoid bridges over fast water, follow official routes, and never walk or drive through floodwaters.";
  }

  if (text.includes("safety") || text.includes("safe")) {
    return "Flood safety tips: prepare an emergency kit, keep important documents in waterproof bags, unplug electrical devices, and stay tuned to local alerts.";
  }

  if (text.includes("route") || text.includes("road") || text.includes("way out")) {
    return "Use main roads to reach designated shelters or high ground. Avoid low-lying roads, underpasses, and areas near rivers or drains.";
  }

  if (text.includes("before flood") || text.includes("prepare") || text.includes("readiness")) {
    return "Before floods: know your risk zone, prepare go-bags, identify evacuation routes, store clean water and non-perishable food, and keep a battery radio.";
  }

  if (text.includes("during flood") || text.includes("now")) {
    return "During floods: move to higher floors, avoid contact with water, don't use elevators, and listen to government advisories.";
  }

  if (text.includes("after flood") || text.includes("post flood")) {
    return "After floods: return home only when declared safe, avoid contaminated water, check for structural damage, and document losses for insurance.";
  }

  if (text.includes("risk") || text.includes("probability")) {
    return "Flood risk depends on rainfall intensity, drainage, river level, soil saturation, and dam conditions. Your dashboard prediction gives a quick estimate.";
  }

  if (text.includes("help")) {
    return "I can help with flood preparedness, safety tips, evacuation guidelines, and understanding risk. Ask me things like: 'How to evacuate safely?' or 'What to do during a flood?'.";
  }

  return "That's a good question. In general, stay informed, avoid floodwaters, move to higher ground, and follow instructions from local authorities. Ask me about evacuation, safety, or flood preparedness for more details.";
}
