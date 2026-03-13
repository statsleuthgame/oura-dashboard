import { useOuraData } from "../hooks/useOuraData";
import PanelWrapper from "./PanelWrapper";
import MetricCard from "./MetricCard";
import StepsCaloriesChart from "./StepsCaloriesChart";
import ActivityBreakdownChart from "./ActivityBreakdownChart";
import { formatNumber, roundTo } from "../lib/formatters";

export default function ActivityPanel() {
  const { data, loading, error } = useOuraData("/activity");

  const summary = data?.summary;
  const daily = data?.daily || [];

  return (
    <PanelWrapper title="Activity" loading={loading} error={error}>
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <MetricCard
          label="Avg Score"
          value={summary?.avg_score}
          color="text-oura-yellow"
        />
        <MetricCard
          label="Total Steps"
          value={summary?.total_steps ? formatNumber(summary.total_steps) : null}
          color="text-oura-green"
        />
        <MetricCard
          label="Avg Calories"
          value={roundTo(summary?.avg_calories)}
          unit="cal"
          color="text-oura-red"
        />
        <MetricCard
          label="Active Minutes"
          value={roundTo(summary?.total_active_minutes)}
          unit="min"
          color="text-oura-blue"
        />
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <StepsCaloriesChart data={daily} />
        <ActivityBreakdownChart data={daily} />
      </div>
    </PanelWrapper>
  );
}
