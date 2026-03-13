import {
  ResponsiveContainer, AreaChart, Area, LineChart, Line,
  XAxis, YAxis, CartesianGrid, Tooltip,
} from "recharts";
import { COLORS, tooltipStyle, gridStyle, axisStyle } from "../lib/chartTheme";
import { formatDate } from "../lib/formatters";

export default function AppleHrTrendChart({ data }) {
  return (
    <div className="bg-white/5 backdrop-blur border border-white/10 rounded-2xl p-5">
      <h3 className="text-sm font-medium text-gray-400 mb-4">Heart Rate Trend</h3>
      <ResponsiveContainer width="100%" height={240}>
        <AreaChart data={data}>
          <defs>
            <linearGradient id="hrRangeGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor={COLORS.appleRed} stopOpacity={0.15} />
              <stop offset="95%" stopColor={COLORS.appleRed} stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid {...gridStyle} />
          <XAxis dataKey="day" tickFormatter={formatDate} {...axisStyle} />
          <YAxis domain={["auto", "auto"]} {...axisStyle} />
          <Tooltip
            {...tooltipStyle}
            labelFormatter={formatDate}
            formatter={(v, name) => [`${Math.round(v)} bpm`, name === "avg_hr" ? "Avg" : name === "min_hr" ? "Min" : "Max"]}
          />
          <Area type="monotone" dataKey="max_hr" stroke="transparent" fill="url(#hrRangeGrad)" />
          <Area type="monotone" dataKey="min_hr" stroke="transparent" fill="#0F1117" />
          <Line type="monotone" dataKey="avg_hr" stroke={COLORS.appleRed} strokeWidth={2} dot={false} />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
