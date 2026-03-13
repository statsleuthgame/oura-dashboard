import { useOuraData } from "../hooks/useOuraData";
import PanelWrapper from "./PanelWrapper";
import MetricCard from "./MetricCard";
import AppleWorkoutTypesChart from "./AppleWorkoutTypesChart";
import AppleWorkoutList from "./AppleWorkoutList";
import { formatNumber, formatMinutes, roundTo } from "../lib/formatters";

export default function AppleWorkoutsPanel() {
  const { data, loading, error } = useOuraData("/apple/workouts");

  const summary = data?.summary;

  return (
    <PanelWrapper title="Workouts" loading={loading} error={error}>
      <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
        <MetricCard
          label="Total Workouts"
          value={summary?.total_workouts}
          color="text-apple-green"
        />
        <MetricCard
          label="Total Duration"
          value={summary?.total_duration_min ? formatMinutes(summary.total_duration_min) : null}
          color="text-apple-orange"
        />
        <MetricCard
          label="Total Calories"
          value={summary?.total_calories ? formatNumber(Math.round(summary.total_calories)) : null}
          unit="cal"
          color="text-apple-red"
        />
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <AppleWorkoutTypesChart data={data?.by_type || []} />
        <AppleWorkoutList workouts={data?.workouts || []} />
      </div>
    </PanelWrapper>
  );
}
