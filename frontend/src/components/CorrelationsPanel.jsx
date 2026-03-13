import { useOuraData } from "../hooks/useOuraData";
import PanelWrapper from "./PanelWrapper";
import CorrelationHeatmap from "./CorrelationHeatmap";

const METRIC_LABELS = {
  sleep_score: "Sleep Score",
  total_sleep: "Total Sleep",
  deep_sleep: "Deep Sleep",
  efficiency: "Efficiency",
  readiness_score: "Readiness",
  hrv_balance: "HRV Balance Score",
  resting_heart_rate: "Resting HR Score",
  activity_score: "Activity Score",
  steps: "Steps",
  active_calories: "Active Cal",
  apple_avg_hr: "Avg HR",
  apple_hrv: "HRV",
  apple_resting_hr: "Resting HR",
  apple_steps: "Steps",
  apple_active_cal: "Active Cal",
};

export default function CorrelationsPanel() {
  const { data, loading, error } = useOuraData("/correlations");

  const topPairs = (data?.pairs || []).slice(0, 5);

  return (
    <PanelWrapper title="Correlations" loading={loading} error={error}>
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div className="lg:col-span-2">
          <CorrelationHeatmap matrix={data?.matrix || {}} />
        </div>
        <div className="bg-white/5 backdrop-blur border border-white/10 rounded-2xl p-5">
          <h3 className="text-sm font-medium text-gray-400 mb-4">
            Strongest Correlations
          </h3>
          <div className="space-y-3">
            {topPairs.map((pair, i) => (
              <div
                key={i}
                className="flex items-center justify-between text-sm"
              >
                <span className="text-gray-300 truncate mr-2">
                  {METRIC_LABELS[pair.metric_a] || pair.metric_a}{" "}
                  <span className="text-gray-600">vs</span>{" "}
                  {METRIC_LABELS[pair.metric_b] || pair.metric_b}
                </span>
                <span
                  className={`font-mono font-medium ${
                    pair.r > 0 ? "text-oura-green" : "text-oura-blue"
                  }`}
                >
                  {pair.r > 0 ? "+" : ""}
                  {pair.r.toFixed(3)}
                </span>
              </div>
            ))}
            {topPairs.length === 0 && (
              <p className="text-gray-600 text-sm">
                Not enough data yet. Try a longer range.
              </p>
            )}
          </div>
        </div>
      </div>
    </PanelWrapper>
  );
}
