import {
  ResponsiveContainer, LineChart, Line,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend,
} from "recharts";
import { COLORS, tooltipStyle, gridStyle, axisStyle } from "../lib/chartTheme";
import { formatDate, roundTo } from "../lib/formatters";

export default function AppleVitalsChart({ respiratoryData, spo2Data }) {
  // Merge both datasets by day
  const byDay = {};
  for (const r of respiratoryData || []) {
    byDay[r.day] = { day: r.day, avg_rate: r.avg_rate };
  }
  for (const r of spo2Data || []) {
    if (!byDay[r.day]) byDay[r.day] = { day: r.day };
    byDay[r.day].avg_spo2 = r.avg_spo2;
  }
  const merged = Object.values(byDay).sort((a, b) => a.day.localeCompare(b.day));

  return (
    <div className="bg-white/5 backdrop-blur border border-white/10 rounded-2xl p-5">
      <h3 className="text-sm font-medium text-gray-400 mb-4">Vitals Trend</h3>
      <ResponsiveContainer width="100%" height={240}>
        <LineChart data={merged}>
          <CartesianGrid {...gridStyle} />
          <XAxis dataKey="day" tickFormatter={formatDate} {...axisStyle} />
          <YAxis yAxisId="rate" orientation="left" {...axisStyle} />
          <YAxis yAxisId="spo2" orientation="right" domain={[90, 100]} {...axisStyle} />
          <Tooltip
            {...tooltipStyle}
            labelFormatter={formatDate}
            formatter={(v, name) => [
              `${roundTo(v, 1)}${name === "avg_spo2" ? "%" : " br/min"}`,
              name === "avg_spo2" ? "SpO2" : "Respiratory Rate",
            ]}
          />
          <Legend wrapperStyle={{ fontSize: "12px", color: "#9ca3af" }} />
          <Line
            yAxisId="rate"
            type="monotone"
            dataKey="avg_rate"
            name="Resp Rate"
            stroke={COLORS.cyan}
            strokeWidth={2}
            dot={false}
          />
          <Line
            yAxisId="spo2"
            type="monotone"
            dataKey="avg_spo2"
            name="SpO2"
            stroke={COLORS.appleBlue}
            strokeWidth={2}
            dot={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
