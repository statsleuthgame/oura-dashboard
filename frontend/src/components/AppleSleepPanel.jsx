import { useOuraData } from "../hooks/useOuraData";
import PanelWrapper from "./PanelWrapper";
import MetricCard from "./MetricCard";
import AppleSleepStagesChart from "./AppleSleepStagesChart";
import { formatMinutes } from "../lib/formatters";

export default function AppleSleepPanel() {
  const { data, loading, error } = useOuraData("/apple/sleep");

  const summary = data?.summary;

  return (
    <PanelWrapper title="Sleep" loading={loading} error={error}>
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <MetricCard
          label="Avg Total Sleep"
          value={summary?.avg_total_sleep ? formatMinutes(summary.avg_total_sleep) : null}
          color="text-apple-blue"
        />
        <MetricCard
          label="Avg Deep"
          value={summary?.avg_deep ? formatMinutes(summary.avg_deep) : null}
          color="text-apple-cyan"
        />
        <MetricCard
          label="Avg REM"
          value={summary?.avg_rem ? formatMinutes(summary.avg_rem) : null}
          color="text-oura-purple"
        />
        <MetricCard
          label="Nights Tracked"
          value={summary?.total_nights}
          color="text-white"
        />
      </div>
      <AppleSleepStagesChart data={data?.daily || []} />
    </PanelWrapper>
  );
}
