
async function calculateVegetation() {
    const result = document.getElementById("vegetationResult");

    const nir = document.getElementById("nirInput").valueAsNumber;
    const red = document.getElementById("redInput").valueAsNumber;
    const blue = document.getElementById("blueInput").valueAsNumber;

    const values = [nir, red, blue];

    if (values.some(v => !Number.isFinite(v) || v < 0 || v > 1)) {
        result.textContent = "Enter values between 0 and 1.";
        return;
    }

    result.textContent = "Analyzing vegetation...";

    try {
        const response = await fetch("/api/vegetation", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ nir, red, blue })
        });

        const output = await response.json();

        if (!response.ok || output.status !== "success") {
            throw new Error(output.message || "Analysis failed");
        }

        const data = output.data;

        result.textContent = "";

        const rows = [
            ["NDVI", data.ndvi],
            ["EVI", data.evi],
            ["SAVI", data.savi],
            ["Status", data.health_status]
        ];

        for (const [label, value] of rows) {
            const line = document.createElement("div");
            line.textContent = `${label}: ${value ?? "N/A"}`;
            result.appendChild(line);
        }

    } catch (error) {
        result.textContent = "Error: " + error.message;
    }
}

async function analyzeSensors() {

    const result = document.getElementById("sensorResult");

    const data = {
        moisture: document.getElementById("soilMoisture").valueAsNumber,
        temperature: document.getElementById("temperature").valueAsNumber,
        humidity: document.getElementById("humidity").valueAsNumber,
        leaf_wetness: document.getElementById("leafWetness").valueAsNumber
    };

    if (Object.values(data).some(v => !Number.isFinite(v))) {
        result.textContent = "Enter valid sensor readings.";
        return;
    }

    result.textContent = "Analyzing sensor data...";

    try {

        const response = await fetch("/api/sensors", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(data)
        });

        const output = await response.json();

        if (!response.ok || output.status !== "success") {
            throw new Error(output.message || "Analysis failed");
        }

        const sensor = output.data;

        result.textContent = "";

        const rows = [
            ["Soil Moisture", sensor.moisture + "%"],
            ["Temperature", sensor.temperature + " °C"],
            ["Humidity", sensor.humidity + "%"],
            ["Leaf Wetness", sensor.leaf_wetness + "%"],
            ["Risk Score", sensor.risk_score + "/100"],
            ["Risk Level", sensor.risk_level],
            ["Method", sensor.method],
            ["Alerts", sensor.alerts.join(", ") || "No alerts"]
        ];

        for (const [label, value] of rows) {
            const line = document.createElement("div");
            line.textContent = `${label}: ${value}`;
            result.appendChild(line);
        }

    } catch (error) {
        result.textContent = "Error: " + error.message;
    }
}


let liveKalmanChart = null;


async function applyKalmanFilter() {

    const result = document.getElementById("kalmanResult");

    const parts = document.getElementById("sensorReadings")
        .value.split(",").map(v => v.trim());

    const readings = parts.map(Number);

    if (parts.some(v => v === "") ||
        readings.some(v => !Number.isFinite(v))) {
        result.textContent = "Enter valid comma-separated numbers.";
        return;
    }

    result.textContent = "Processing sensor readings...";

    try {

        const response = await fetch("/api/sensor-fusion", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ readings })
        });

        const output = await response.json();

        if (!response.ok || output.status !== "success") {
            throw new Error(output.message || "Filtering failed");
        }

        result.textContent = "Sensor filtering completed.";

        if (liveKalmanChart) {
            liveKalmanChart.destroy();
        }

        const ctx = document.getElementById("liveKalmanChart");

        liveKalmanChart = new Chart(ctx, {
            type: "line",

            data: {
                labels: readings.map((_, i) => i + 1),

                datasets: [
                    {
                        label: "Raw Sensor Data",
                        data: output.raw_readings,
                        borderColor: "#f97316",
                        borderDash: [5, 5],
                        tension: 0.2
                    },
                    {
                        label: "Kalman Filter Output",
                        data: output.filtered_readings,
                        borderColor: "#22d474",
                        tension: 0.2
                    }
                ]
            },

            options: {
                responsive: true,
                maintainAspectRatio: false,

                plugins: {
                    legend: {
                        labels: {
                            color: "#e2e8f0"
                        }
                    }
                },

                scales: {
                    x: {
                        ticks: { color: "#94a3b8" }
                    },
                    y: {
                        ticks: { color: "#94a3b8" }
                    }
                }
            }
        });

    } catch (error) {
        result.textContent = "Error: " + error.message;
    }
}
