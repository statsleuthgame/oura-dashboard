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
import { formatDate, formatNumber } from "../lib/formatters";

export default function StepsCaloriesChart({ data }) {
  return (
    <div className="bg-white/5 backdrop-blur border border-white/10 rounded-2xl p-5">
      <h3 className="text-sm font-medium text-gray-400 mb-4">
        Steps & Calories
      </h3>
      <ResponsiveContainer width="100%" height={240}>
        <BarChart data={data}>
          <CartesianGrid {...gridStyle} />
          <XAxis dataKey="day" tickFormatter={formatDate} {...axisStyle} />
          <YAxis yAxisId="steps" orientation="left" {...axisStyle} />
          <YAxis yAxisId="cals" orientation="right" {...axisStyle} />
          <Tooltip
            {...tooltipStyle}
            labelFormatter={formatDate}
            formatter={(value, name) => [
              formatNumber(value),
              name === "steps" ? "Steps" : "Active Cal",
            ]}
          />
          <Legend wrapperStyle={{ fontSize: "12px", color: "#9ca3af" }} />
          <Bar
            yAxisId="steps"
            dataKey="steps"
            name="Steps"
            fill={COLORS.green}
            radius={[4, 4, 0, 0]}
            barSize={16}
          />
          <Bar
            yAxisId="cals"
            dataKey="active_calories"
            name="Active Cal"
            fill={COLORS.yellow}
            radius={[4, 4, 0, 0]}
            barSize={16}
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
