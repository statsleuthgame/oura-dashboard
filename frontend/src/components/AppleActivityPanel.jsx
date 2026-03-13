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
      <div className="grid grid-cols-2 sm:grid-cols-5 gap-4">
        <MetricCard
          label="Avg Daily Steps"
          value={steps?.summary?.avg_daily_steps ? formatNumber(Math.round(steps.summary.avg_daily_steps)) : null}
          color="text-apple-green"
        />
        <MetricCard
          label="Avg Active Cal"
          value={energy?.summary?.avg_active_cal ? formatNumber(Math.round(energy.summary.avg_active_cal)) : null}
          unit="cal"
          color="text-apple-red"
        />
        <MetricCard
          label="Avg Total Cal"
          value={energy?.summary?.avg_total_cal ? formatNumber(Math.round(energy.summary.avg_total_cal)) : null}
          unit="cal"
          color="text-apple-orange"
        />
        <MetricCard
          label="Avg Distance"
          value={steps?.summary?.avg_distance ? `${(steps.summary.avg_distance * 0.621371).toFixed(1)}` : null}
          unit="mi"
          color="text-apple-blue"
        />
        <MetricCard
          label="Total Flights"
          value={steps?.summary?.total_flights ? formatNumber(steps.summary.total_flights) : null}
          color="text-white"
        />
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <AppleStepsChart data={steps?.daily || []} />
        <AppleEnergyChart data={energy?.daily || []} />
      </div>
    </PanelWrapper>
  );
}
