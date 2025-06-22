const contractAddress = "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"; // Ganti sesuai kontrak Ganache
const abiPath = "abi/SensorStorage.abi";

let chart;

async function loadSensorData() {
  const statusEl = document.getElementById("status");
  if (statusEl) statusEl.textContent = "🟡 Menghubungkan ke MetaMask...";

  try {
    const abiRes = await fetch(abiPath);
    const abi = await abiRes.json();

    const provider = new ethers.BrowserProvider(window.ethereum);
    await provider.send("eth_requestAccounts", []);
    const signer = await provider.getSigner();
    const contract = new ethers.Contract(contractAddress, abi, provider).connect(signer);

    if (statusEl) statusEl.textContent = "🟢 Terhubung ke MetaMask";

    const filter = contract.filters.DataStored();
    const events = await contract.queryFilter(filter, 0, "latest");
    

    const tableBody = document.querySelector("#sensorTable tbody");
    tableBody.innerHTML = "";

    const labels = [];
    const temps = [];
    const hums = [];

    events.forEach((e) => {
      const data = e.args;
      const timeStr = new Date(Number(data.timestamp) * 1000).toLocaleString();
      const temp = Number(data.temperature) / 100;
      const hum = Number(data.humidity) / 100;

      tableBody.innerHTML += `
        <tr>
          <td>${timeStr}</td>
          <td>${data.sensorId}</td>
          <td>${data.location}</td>
          <td>${data.stage}</td>
          <td>${temp.toFixed(2)}</td>
          <td>${hum.toFixed(2)}</td>
        </tr>
      `;

      labels.push(timeStr);
      temps.push(temp);
      hums.push(hum);
    });

    renderChart(labels, temps, hums);
  } catch (err) {
    console.error("❌ Gagal memuat data:", err);
    if (statusEl) statusEl.textContent = "❌ Gagal terhubung ke MetaMask atau memuat data";
  }
}

function renderChart(labels, temps, hums) {
  const ctx = document.getElementById("chart").getContext("2d");

  if (chart) chart.destroy();

  chart = new Chart(ctx, {
    type: "line",
    data: {
      labels,
      datasets: [
        {
          label: "Suhu (°C)",
          data: temps,
          borderColor: "#16a34a",
          backgroundColor: "rgba(22, 163, 74, 0.2)",
          fill: true,
          tension: 0.4
        },
        {
          label: "Kelembaban (%)",
          data: hums,
          borderColor: "#0ea5e9",
          backgroundColor: "rgba(14, 165, 233, 0.2)",
          fill: true,
          tension: 0.4
        }
      ]
    },
    options: {
      responsive: true,
      plugins: {
        legend: {
          labels: {
            color: "#1f2937",
            font: { size: 14, weight: "bold" }
          }
        }
      },
      scales: {
        x: {
          ticks: { color: "#1f2937" }
        },
        y: {
          beginAtZero: true,
          ticks: { color: "#1f2937" }
        }
      }
    }
  });
}

