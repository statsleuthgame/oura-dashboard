import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from "recharts";
import { COLORS, tooltipStyle, gridStyle, axisStyle } from "../lib/chartTheme";
import { formatDate } from "../lib/formatters";

export default function HrvTrendChart({ data }) {
  return (
    <div className="bg-white/5 backdrop-blur border border-white/10 rounded-2xl p-5">
      <h3 className="text-sm font-medium text-gray-400 mb-4">HRV Balance Score</h3>
      <ResponsiveContainer width="100%" height={240}>
        <AreaChart data={data}>
          <defs>
            <linearGradient id="hrvGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor={COLORS.teal} stopOpacity={0.3} />
              <stop offset="95%" stopColor={COLORS.teal} stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid {...gridStyle} />
          <XAxis dataKey="day" tickFormatter={formatDate} {...axisStyle} />
          <YAxis {...axisStyle} />
          <Tooltip {...tooltipStyle} labelFormatter={formatDate} />
          <Area
            type="monotone"
            dataKey="hrv_balance"
            stroke={COLORS.teal}
            strokeWidth={2}
            fill="url(#hrvGradient)"
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
