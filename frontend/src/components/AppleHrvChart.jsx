import {
  ResponsiveContainer, AreaChart, Area,
  XAxis, YAxis, CartesianGrid, Tooltip,
} from "recharts";
import { COLORS, tooltipStyle, gridStyle, axisStyle } from "../lib/chartTheme";
import { formatDate } from "../lib/formatters";

export default function AppleHrvChart({ data }) {
  return (
    <div className="bg-white/5 backdrop-blur border border-white/10 rounded-2xl p-5">
      <h3 className="text-sm font-medium text-gray-400 mb-4">HRV (SDNN)</h3>
      <ResponsiveContainer width="100%" height={240}>
        <AreaChart data={data}>
          <defs>
            <linearGradient id="appleHrvGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor={COLORS.cyan} stopOpacity={0.3} />
              <stop offset="95%" stopColor={COLORS.cyan} stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid {...gridStyle} />
          <XAxis dataKey="day" tickFormatter={formatDate} {...axisStyle} />
          <YAxis {...axisStyle} />
          <Tooltip
            {...tooltipStyle}
            labelFormatter={formatDate}
            formatter={(v) => [`${Math.round(v)} ms`, "HRV"]}
          />
          <Area
            type="monotone"
            dataKey="avg_hrv"
            stroke={COLORS.cyan}
            strokeWidth={2}
            fill="url(#appleHrvGrad)"
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
