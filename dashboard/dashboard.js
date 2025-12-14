async function loadDashboard() {
    const res = await fetch("/api/dashboard-data");
    const j = await res.json();
  
    const tbody = document.getElementById("farmRows");
    tbody.innerHTML = "";
  
    for (const f of j.farms) {
      const badge =
        f.status === "healthy" ? "bg-success" :
        f.status === "warning" ? "bg-warning text-dark" :
        "bg-danger";
  
      tbody.innerHTML += `
        <tr>
          <td>${f.farm_id}</td>
          <td>${f.farmer}</td>
          <td>${f.crop}</td>
          <td>${f.health_score}</td>
          <td><span class="badge ${badge}">${f.status}</span></td>
          <td class="small">${f.disease_label}</td>
        </tr>
      `;
    }
  
    // Chart
    const ctx = document.getElementById("statusChart");
    new Chart(ctx, {
      type: "bar",
      data: {
        labels: ["healthy", "warning", "critical"],
        datasets: [{
          label: "Farms",
          data: [j.counts.healthy, j.counts.warning, j.counts.critical]
        }]
      },
      options: { responsive: true }
    });
  }
  
  loadDashboard();
  