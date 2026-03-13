import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from "recharts";
import { COLORS, tooltipStyle, gridStyle, axisStyle } from "../lib/chartTheme";
import { formatDate, formatMinutes } from "../lib/formatters";

export default function ActivityBreakdownChart({ data }) {
  return (
    <div className="bg-white/5 backdrop-blur border border-white/10 rounded-2xl p-5">
      <h3 className="text-sm font-medium text-gray-400 mb-4">
        Activity Breakdown
      </h3>
      <ResponsiveContainer width="100%" height={240}>
        <BarChart data={data}>
          <CartesianGrid {...gridStyle} />
          <XAxis dataKey="day" tickFormatter={formatDate} {...axisStyle} />
          <YAxis
            tickFormatter={(v) => `${Math.round(v)}m`}
            {...axisStyle}
          />
          <Tooltip
            {...tooltipStyle}
            labelFormatter={formatDate}
            formatter={(value) => formatMinutes(value)}
          />
          <Legend wrapperStyle={{ fontSize: "12px", color: "#9ca3af" }} />
          <Bar
            dataKey="high_activity_time"
            name="High"
            stackId="act"
            fill={COLORS.red}
          />
          <Bar
            dataKey="medium_activity_time"
            name="Medium"
            stackId="act"
            fill={COLORS.yellow}
          />
          <Bar
            dataKey="low_activity_time"
            name="Low"
            stackId="act"
            fill={COLORS.blue}
            radius={[4, 4, 0, 0]}
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
