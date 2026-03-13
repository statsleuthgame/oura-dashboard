import { useOuraData } from "../hooks/useOuraData";
import PanelWrapper from "./PanelWrapper";
import MetricCard from "./MetricCard";
import AppleHrTrendChart from "./AppleHrTrendChart";
import AppleHrvChart from "./AppleHrvChart";

export default function AppleHeartPanel() {
  const { data: hr, loading: hrLoad, error: hrErr } = useOuraData("/apple/heart-rate");
  const { data: hrv, loading: hrvLoad, error: hrvErr } = useOuraData("/apple/hrv");
  const { data: rhr, loading: rhrLoad, error: rhrErr } = useOuraData("/apple/resting-hr");

  const loading = hrLoad || hrvLoad || rhrLoad;
  const error = hrErr || hrvErr || rhrErr;

  return (
    <PanelWrapper title="Heart" loading={loading} error={error}>
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <MetricCard
          label="Avg Heart Rate"
          value={hr?.summary?.avg_hr}
          unit="bpm"
          color="text-apple-red"
        />
        <MetricCard
          label="Avg Resting HR"
          value={rhr?.summary?.avg_resting_hr}
          unit="bpm"
          color="text-apple-green"
        />
        <MetricCard
          label="Avg HRV"
          value={hrv?.summary?.avg_hrv}
          unit="ms"
          color="text-apple-cyan"
        />
        <MetricCard
          label="Days Tracked"
          value={hr?.summary?.total_days}
          color="text-white"
        />
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <AppleHrTrendChart data={hr?.daily || []} />
        <AppleHrvChart data={hrv?.daily || []} />
      </div>
    </PanelWrapper>
  );
}
