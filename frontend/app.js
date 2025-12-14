const imgInput = document.getElementById("imgInput");
const analyzeBtn = document.getElementById("analyzeBtn");
const previewWrap = document.getElementById("previewWrap");

const diseaseOut = document.getElementById("diseaseOut");
const confOut = document.getElementById("confOut");
const healthOut = document.getElementById("healthOut");
const metricsOut = document.getElementById("metricsOut");

const adviceOut = document.getElementById("adviceOut");
const playBtn = document.getElementById("playBtn");
const audioPlayer = document.getElementById("audioPlayer");

const latEl = document.getElementById("lat");
const lonEl = document.getElementById("lon");

let lastAudioB64 = null;

imgInput.addEventListener("change", () => {
  previewWrap.innerHTML = "";
  const f = imgInput.files?.[0];
  if (!f) return;
  const url = URL.createObjectURL(f);
  previewWrap.innerHTML = `<img src="${url}" class="img-fluid rounded border" />`;
});

analyzeBtn.addEventListener("click", async () => {
  const f = imgInput.files?.[0];
  if (!f) {
    alert("Please select an image.");
    return;
  }

  // Reset UI
  diseaseOut.textContent = "Analyzing...";
  confOut.textContent = "";
  healthOut.textContent = "—";
  metricsOut.textContent = "";
  adviceOut.textContent = "—";
  playBtn.disabled = true;
  audioPlayer.style.display = "none";
  lastAudioB64 = null;

  const fd = new FormData();
  fd.append("image", f);

  const lat = parseFloat(latEl.value);
  const lon = parseFloat(lonEl.value);
  let url = "/api/analyze-image";
  if (!Number.isNaN(lat) && !Number.isNaN(lon)) {
    url += `?lat=${encodeURIComponent(lat)}&lon=${encodeURIComponent(lon)}`;
  }

  const res = await fetch(url, { method: "POST", body: fd });
  const analysis = await res.json();

  diseaseOut.textContent = analysis.disease_label;
  confOut.textContent = `confidence: ${(analysis.confidence * 100).toFixed(1)}%`;
  healthOut.textContent = analysis.health_score.toFixed(1);

  metricsOut.textContent =
    `yellowing: ${analysis.yellowing_pct.toFixed(1)}% | ` +
    `spots: ${analysis.spots_pct.toFixed(1)}% | ` +
    `heatStress: ${analysis.heat_stress_pct.toFixed(1)}%`;

  // Now call recommendation
  const recRes = await fetch("/api/get-recommendation", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      disease_label: analysis.disease_label,
      confidence: analysis.confidence,
      health_score: analysis.health_score,
      yellowing_pct: analysis.yellowing_pct,
      spots_pct: analysis.spots_pct,
      weather: analysis.weather,
      soil: analysis.soil
    })
  });
  const rec = await recRes.json();

  adviceOut.textContent = rec.advice_bn;
  lastAudioB64 = rec.audio_mp3_base64;
  playBtn.disabled = false;
});

playBtn.addEventListener("click", () => {
  if (!lastAudioB64) return;
  const src = `data:audio/mp3;base64,${lastAudioB64}`;
  audioPlayer.src = src;
  audioPlayer.style.display = "block";
  audioPlayer.play();
});

// Voice Query (optional)
const audioInput = document.getElementById("audioInput");
const sttBtn = document.getElementById("sttBtn");
const sttOut = document.getElementById("sttOut");

sttBtn.addEventListener("click", async () => {
  const f = audioInput.files?.[0];
  if (!f) { alert("Select an audio file."); return; }
  const fd = new FormData();
  fd.append("audio", f);

  sttOut.textContent = "Recognizing...";
  const res = await fetch("/api/voice-query", { method: "POST", body: fd });
  const j = await res.json();
  sttOut.textContent = j.text_bn ? `Bangla text: ${j.text_bn}` : (j.error || "No text");
});
