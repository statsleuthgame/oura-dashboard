import { useOuraData } from "../hooks/useOuraData";
import PanelWrapper from "./PanelWrapper";
import MetricCard from "./MetricCard";
import AppleStepsChart from "./AppleStepsChart";
import AppleEnergyChart from "./AppleEnergyChart";
import { formatNumber, roundTo } from "../lib/formatters";

export default function AppleActivityPanel() {
  const { data: steps, loading: stepsLoad, error: stepsErr } = useOuraData("/apple/steps");
  const { data: energy, loading: energyLoad, error: energyErr } = useOuraData("/apple/energy");

  const loading = stepsLoad || energyLoad;
  const error = stepsErr || energyErr;

  return (
    <PanelWrapper title="Activity" loading={loading} error={error}>
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <MetricCard
          label="Avg Daily Steps"
          value={steps?.summary?.avg_daily_steps ? formatNumber(Math.round(steps.summary.avg_daily_steps)) : null}
          color="text-apple-green"
        />
        <MetricCard
          label="Total Steps"
          value={steps?.summary?.total_steps ? formatNumber(steps.summary.total_steps) : null}
          color="text-white"
        />
        <MetricCard
          label="Avg Active Cal"
          value={roundTo(energy?.summary?.avg_active_cal)}
          unit="cal"
          color="text-apple-red"
        />
        <MetricCard
          label="Total Flights"
          value={steps?.summary?.total_flights ? formatNumber(steps.summary.total_flights) : null}
          color="text-apple-orange"
        />
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <AppleStepsChart data={steps?.daily || []} />
        <AppleEnergyChart data={energy?.daily || []} />
      </div>
    </PanelWrapper>
  );
}
