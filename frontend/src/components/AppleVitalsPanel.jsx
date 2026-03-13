import { useOuraData } from "../hooks/useOuraData";
import PanelWrapper from "./PanelWrapper";
import MetricCard from "./MetricCard";
import AppleVitalsChart from "./AppleVitalsChart";
import { roundTo } from "../lib/formatters";

export default function AppleVitalsPanel() {
  const { data: resp, loading: respLoad, error: respErr } = useOuraData("/apple/respiratory");
  const { data: spo2, loading: spo2Load, error: spo2Err } = useOuraData("/apple/spo2");

  const loading = respLoad || spo2Load;
  const error = respErr || spo2Err;

  return (
    <PanelWrapper title="Vitals" loading={loading} error={error}>
      <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
        <MetricCard
          label="Avg Respiratory Rate"
          value={roundTo(resp?.summary?.avg_respiratory_rate)}
          unit="br/min"
          color="text-apple-cyan"
        />
        <MetricCard
          label="Avg SpO2"
          value={roundTo(spo2?.summary?.avg_spo2)}
          unit="%"
          color="text-apple-blue"
        />
        <MetricCard
          label="Min SpO2"
          value={roundTo(spo2?.summary?.min_spo2)}
          unit="%"
          color="text-apple-orange"
        />
      </div>
      <AppleVitalsChart
        respiratoryData={resp?.daily || []}
        spo2Data={spo2?.daily || []}
      />
    </PanelWrapper>
  );
}
