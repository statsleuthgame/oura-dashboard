import { useOuraData } from "../hooks/useOuraData";
import PanelWrapper from "./PanelWrapper";
import MetricCard from "./MetricCard";
import ReadinessScoreChart from "./ReadinessScoreChart";
import HrvTrendChart from "./HrvTrendChart";

export default function HrvReadinessPanel() {
  const { data: readiness, loading, error } = useOuraData("/readiness");

  const summary = readiness?.summary;
  const daily = readiness?.daily || [];

  return (
    <PanelWrapper title="HRV & Readiness" loading={loading} error={error}>
      <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
        <MetricCard
          label="Avg Readiness"
          value={summary?.avg_score}
          color="text-oura-green"
        />
        <MetricCard
          label="HRV Balance Score"
          value={summary?.avg_hrv_balance}
          unit="/100"
          color="text-teal-400"
        />
        <MetricCard
          label="Resting HR Score"
          value={summary?.avg_resting_hr}
          unit="/100"
          color="text-oura-red"
        />
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <ReadinessScoreChart data={daily} />
        <HrvTrendChart data={daily} />
      </div>
    </PanelWrapper>
  );
}
