import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from "recharts";
import { COLORS, tooltipStyle, gridStyle, axisStyle } from "../lib/chartTheme";
import { formatDate } from "../lib/formatters";

export default function HeartRateChart({ data }) {
  if (!data || data.length === 0) return null;

  const formatTs = (ts) => {
    if (!ts) return "";
    // If it's a date-only string (daily avg)
    if (ts.length === 10) return formatDate(ts);
    // Otherwise show time
    const d = new Date(ts);
    return d.toLocaleTimeString("en-US", { hour: "numeric", minute: "2-digit" });
  };

  return (
    <div className="bg-white/5 backdrop-blur border border-white/10 rounded-2xl p-5">
      <h3 className="text-sm font-medium text-gray-400 mb-4">Heart Rate</h3>
      <ResponsiveContainer width="100%" height={240}>
        <LineChart data={data}>
          <CartesianGrid {...gridStyle} />
          <XAxis dataKey="timestamp" tickFormatter={formatTs} {...axisStyle} />
          <YAxis domain={["auto", "auto"]} {...axisStyle} />
          <Tooltip
            {...tooltipStyle}
            labelFormatter={formatTs}
            formatter={(v) => [`${v} bpm`, "Heart Rate"]}
          />
          <Line
            type="monotone"
            dataKey="bpm"
            stroke={COLORS.red}
            strokeWidth={1.5}
            dot={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
