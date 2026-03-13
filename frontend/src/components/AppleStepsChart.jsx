import {
  ResponsiveContainer, BarChart, Bar,
  XAxis, YAxis, CartesianGrid, Tooltip,
} from "recharts";
import { COLORS, tooltipStyle, gridStyle, axisStyle } from "../lib/chartTheme";
import { formatDate, formatNumber } from "../lib/formatters";

export default function AppleStepsChart({ data }) {
  return (
    <div className="bg-white/5 backdrop-blur border border-white/10 rounded-2xl p-5">
      <h3 className="text-sm font-medium text-gray-400 mb-4">Daily Steps</h3>
      <ResponsiveContainer width="100%" height={240}>
        <BarChart data={data}>
          <CartesianGrid {...gridStyle} />
          <XAxis dataKey="day" tickFormatter={formatDate} {...axisStyle} />
          <YAxis tickFormatter={(v) => `${(v / 1000).toFixed(0)}k`} {...axisStyle} />
          <Tooltip
            {...tooltipStyle}
            labelFormatter={formatDate}
            formatter={(v) => [formatNumber(Math.round(v)), "Steps"]}
          />
          <Bar
            dataKey="steps"
            fill={COLORS.appleGreen}
            radius={[4, 4, 0, 0]}
            barSize={12}
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
