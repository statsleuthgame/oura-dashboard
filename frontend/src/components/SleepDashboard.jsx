import { useOuraData } from "../hooks/useOuraData";
import PanelWrapper from "./PanelWrapper";
import MetricCard from "./MetricCard";
import SleepScoreChart from "./SleepScoreChart";
import SleepStagesChart from "./SleepStagesChart";
import { formatMinutes } from "../lib/formatters";

export default function SleepDashboard() {
  const { data, loading, error } = useOuraData("/sleep");

  const summary = data?.summary;
  const daily = data?.daily || [];

  // Compute average total sleep for display
  const avgSleep =
    daily.length > 0
      ? daily.reduce((sum, d) => sum + (d.total_sleep || 0), 0) / daily.length
      : null;

  return (
    <PanelWrapper title="Sleep" loading={loading} error={error}>
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <MetricCard
          label="Avg Score"
          value={summary?.avg_score}
          color="text-oura-blue"
        />
        <MetricCard
          label="Avg Efficiency"
          value={summary?.avg_efficiency}
          unit="%"
          color="text-oura-green"
        />
        <MetricCard
          label="Avg Duration"
          value={avgSleep ? formatMinutes(avgSleep) : null}
          color="text-oura-purple"
        />
        <MetricCard
          label="Nights Tracked"
          value={summary?.total_nights}
          color="text-white"
        />
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <SleepScoreChart data={daily} />
        <SleepStagesChart data={daily} />
      </div>
    </PanelWrapper>
  );
}
