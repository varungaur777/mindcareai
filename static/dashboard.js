document.addEventListener("DOMContentLoaded", () => {
    if (!window.dashboardData) return;

    const {labels, scores, moodCounts} = window.dashboardData;

    const lineCtx = document.getElementById("moodLineChart");
    if (lineCtx && labels.length > 0) {
        new Chart(lineCtx, {
            type: "line",
            data: {
                labels,
                datasets: [{
                    label: "Mood Score",
                    data: scores,
                    borderColor: "#2dd4bf",
                    backgroundColor: "rgba(45, 212, 191, 0.15)",
                    tension: 0.3,
                    fill: true
                }]
            },
            options: {
                scales: {
                    y: {beginAtZero: true, max: 100}
                }
            }
        });
    }

    const pieCtx = document.getElementById("moodPieChart");
    const moodLabels = Object.keys(moodCounts || {});
    const moodValues = Object.values(moodCounts || {});
    if (pieCtx && moodLabels.length > 0) {
        new Chart(pieCtx, {
            type: "doughnut",
            data: {
                labels: moodLabels,
                datasets: [{
                    data: moodValues,
                    backgroundColor: [
                        "#22c55e",
                        "#2dd4bf",
                        "#38bdf8",
                        "#f97316",
                        "#ef4444"
                    ]
                }]
            },
            options: {
                plugins: {
                    legend: {position: "bottom"}
                }
            }
        });
    }
});
