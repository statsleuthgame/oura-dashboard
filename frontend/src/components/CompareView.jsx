import { useCompareData } from "../hooks/useCompareData";
import { useUser } from "../context/UserContext";
import { useDateRange } from "../context/DateRangeContext";
import CompareChart from "./CompareChart";
import { formatMinutes, periodLabel } from "../lib/formatters";

const SLEEP_TOTAL_KEY = (row) =>
  row.total_sleep != null ? Math.round((row.total_sleep / 60) * 10) / 10 : null;

const STEPS_KEY = (row) => row.value ?? row.steps ?? null;

const STEP_TITLES = { day: "Daily Steps", wk: "Weekly Avg Steps", mo: "Monthly Avg Steps" };

export default function CompareView() {
  const { users } = useUser();
  const { days } = useDateRange();

  const sleep = useCompareData("/sleep", "score");
  const sleepDuration = useCompareData("/sleep", SLEEP_TOTAL_KEY);
  const readiness = useCompareData("/readiness", "score");
  const hrv = useCompareData("/apple/hrv", "avg_hrv");
  const rhr = useCompareData("/apple/resting-hr", "resting_hr");
  const steps = useCompareData("/apple/steps", STEPS_KEY);

  const anyLoading =
    sleep.loading || sleepDuration.loading || readiness.loading ||
    hrv.loading || rhr.loading || steps.loading;

  if (users.length < 2) {
    return (
      <div className="text-center py-20 text-gray-500">
        Compare view requires two users.
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-3">
        <div className="w-6 h-6 rounded-full bg-gradient-to-br from-oura-blue to-[#FF2D55] flex items-center justify-center">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2.5" strokeLinecap="round">
            <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />
            <circle cx="9" cy="7" r="4" />
            <path d="M22 21v-2a4 4 0 0 0-3-3.87" />
            <path d="M16 3.13a4 4 0 0 1 0 7.75" />
          </svg>
        </div>
        <h2 className="text-sm font-medium text-gray-500 uppercase tracking-wider">
          Compare
        </h2>
        <div className="flex items-center gap-2 ml-auto">
          <UserLegend />
        </div>
      </div>

      {anyLoading && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <div key={i} className="h-[320px] bg-white/5 rounded-2xl animate-pulse" />
          ))}
        </div>
      )}

      {!anyLoading && (
        <>
          {/* Summary cards */}
          <CompareSummaryCards
            sleep={sleep.data}
            steps={steps.data}
            rhr={rhr.data}
            hrv={hrv.data}
            users={users}
          />

          {/* Charts */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <CompareChart
              data={sleep.data}
              title="Sleep Score"
              domain={[0, 100]}
            />
            <CompareChart
              data={sleepDuration.data}
              title="Total Sleep"
              unit="h"
            />
            <CompareChart
              data={readiness.data}
              title="Readiness Score"
              domain={[0, 100]}
            />
            <CompareChart
              data={steps.data}
              title={STEP_TITLES[periodLabel(days)]}
              formatter={(v) => v?.toLocaleString()}
            />
            <CompareChart
              data={rhr.data}
              title="Resting Heart Rate"
              unit=" bpm"
            />
            <CompareChart
              data={hrv.data}
              title="Heart Rate Variability"
              unit=" ms"
            />
          </div>
        </>
      )}
    </div>
  );
}

function UserLegend() {
  const { users } = useUser();
  const colors = { cody: "#4A90D9", stef: "#FF2D55" };

  return (
    <div className="flex items-center gap-4">
      {users.map((u) => (
        <div key={u.key} className="flex items-center gap-1.5">
          <div
            className="w-3 h-3 rounded-full"
            style={{ backgroundColor: colors[u.key] || "#888" }}
          />
          <span className="text-sm text-gray-400">{u.name}</span>
        </div>
      ))}
    </div>
  );
}

function CompareSummaryCards({ sleep, steps, rhr, hrv, users }) {
  const metrics = [
    { label: "Sleep Score", data: sleep, unit: "" },
    { label: "Steps", data: steps, unit: "" },
    { label: "Resting HR", data: rhr, unit: " bpm" },
    { label: "HRV", data: hrv, unit: " ms" },
  ];

  const colors = { cody: "#4A90D9", stef: "#FF2D55" };

  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
      {metrics.map((m) => {
        const avgs = {};
        if (m.data) {
          for (const u of users) {
            const vals = m.data
              .map((d) => d[u.key])
              .filter((v) => v != null);
            avgs[u.key] = vals.length > 0
              ? Math.round(vals.reduce((a, b) => a + b, 0) / vals.length)
              : null;
          }
        }

        return (
          <div
            key={m.label}
            className="bg-white/5 backdrop-blur border border-white/10 rounded-2xl p-5"
          >
            <p className="text-sm text-gray-400 mb-3">{m.label}</p>
            <div className="space-y-1.5">
              {users.map((u) => (
                <div key={u.key} className="flex items-center justify-between">
                  <span className="text-xs text-gray-500">{u.name}</span>
                  <span
                    className="text-lg font-bold"
                    style={{ color: colors[u.key] }}
                  >
                    {avgs[u.key] != null
                      ? `${avgs[u.key].toLocaleString()}${m.unit}`
                      : "--"}
                  </span>
                </div>
              ))}
            </div>
          </div>
        );
      })}
    </div>
  );
}
