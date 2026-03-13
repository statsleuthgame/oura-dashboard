const METRIC_LABELS = {
  sleep_score: "Sleep Score",
  total_sleep: "Total Sleep",
  deep_sleep: "Deep Sleep",
  efficiency: "Efficiency",
  readiness_score: "Readiness",
  hrv_balance: "HRV Balance",
  resting_heart_rate: "Resting HR",
  activity_score: "Activity Score",
  steps: "Steps",
  active_calories: "Active Cal",
  apple_avg_hr: "Avg HR",
  apple_hrv: "HRV",
  apple_resting_hr: "Resting HR",
  apple_steps: "Steps",
  apple_active_cal: "Active Cal",
};

function getColor(r) {
  if (r === null || r === undefined) return "rgba(255,255,255,0.03)";
  const abs = Math.abs(r);
  if (r > 0) {
    // Green
    return `rgba(39, 174, 96, ${abs * 0.7 + 0.05})`;
  }
  // Blue
  return `rgba(74, 144, 217, ${abs * 0.7 + 0.05})`;
}

export default function CorrelationHeatmap({ matrix }) {
  const metrics = Object.keys(matrix || {});

  return (
    <div className="bg-white/5 backdrop-blur border border-white/10 rounded-2xl p-5 overflow-x-auto">
      <h3 className="text-sm font-medium text-gray-400 mb-4">
        Correlation Matrix
      </h3>
      <div
        className="grid gap-1"
        style={{
          gridTemplateColumns: `100px repeat(${metrics.length}, 1fr)`,
          minWidth: `${100 + metrics.length * 64}px`,
        }}
      >
        {/* Header row */}
        <div />
        {metrics.map((m) => (
          <div
            key={m}
            className="text-[10px] text-gray-500 text-center truncate px-1"
            title={METRIC_LABELS[m]}
          >
            {METRIC_LABELS[m]}
          </div>
        ))}

        {/* Data rows */}
        {metrics.map((rowKey) => (
          <>
            <div
              key={`label-${rowKey}`}
              className="text-[11px] text-gray-400 flex items-center truncate pr-2"
              title={METRIC_LABELS[rowKey]}
            >
              {METRIC_LABELS[rowKey]}
            </div>
            {metrics.map((colKey) => {
              const r =
                rowKey === colKey
                  ? 1.0
                  : matrix?.[rowKey]?.[colKey];
              return (
                <div
                  key={`${rowKey}-${colKey}`}
                  className="aspect-square rounded-md flex items-center justify-center text-[10px] font-mono cursor-default transition-transform hover:scale-110"
                  style={{ backgroundColor: getColor(r) }}
                  title={`${METRIC_LABELS[rowKey]} vs ${METRIC_LABELS[colKey]}: r=${r !== null && r !== undefined ? r.toFixed(3) : "N/A"}`}
                >
                  {r !== null && r !== undefined ? r.toFixed(2) : ""}
                </div>
              );
            })}
          </>
        ))}
      </div>

      {/* Legend */}
      <div className="flex items-center justify-center gap-4 mt-4 text-[11px] text-gray-500">
        <div className="flex items-center gap-1.5">
          <div className="w-3 h-3 rounded-sm bg-[rgba(74,144,217,0.6)]" />
          <span>Negative</span>
        </div>
        <div className="flex items-center gap-1.5">
          <div className="w-3 h-3 rounded-sm bg-[rgba(255,255,255,0.03)]" />
          <span>None</span>
        </div>
        <div className="flex items-center gap-1.5">
          <div className="w-3 h-3 rounded-sm bg-[rgba(39,174,96,0.6)]" />
          <span>Positive</span>
        </div>
      </div>
    </div>
  );
}
