import {
  ResponsiveContainer, BarChart, Bar,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend,
} from "recharts";
import { COLORS, tooltipStyle, gridStyle, axisStyle } from "../lib/chartTheme";
import { formatDate, formatMinutes } from "../lib/formatters";

export default function AppleSleepStagesChart({ data }) {
  return (
    <div className="bg-white/5 backdrop-blur border border-white/10 rounded-2xl p-5">
      <h3 className="text-sm font-medium text-gray-400 mb-4">Sleep Stages</h3>
      <ResponsiveContainer width="100%" height={280}>
        <BarChart data={data}>
          <CartesianGrid {...gridStyle} />
          <XAxis dataKey="day" tickFormatter={formatDate} {...axisStyle} />
          <YAxis tickFormatter={(v) => `${Math.round(v / 60)}h`} {...axisStyle} />
          <Tooltip
            {...tooltipStyle}
            labelFormatter={formatDate}
            formatter={(value) => formatMinutes(value)}
          />
          <Legend wrapperStyle={{ fontSize: "12px", color: "#9ca3af" }} />
          <Bar dataKey="deep" name="Deep" stackId="sleep" fill={COLORS.appleBlue} />
          <Bar dataKey="rem" name="REM" stackId="sleep" fill={COLORS.purple} />
          <Bar dataKey="core" name="Core" stackId="sleep" fill={COLORS.cyan} />
          <Bar dataKey="awake" name="Awake" stackId="sleep" fill={COLORS.orange} radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
