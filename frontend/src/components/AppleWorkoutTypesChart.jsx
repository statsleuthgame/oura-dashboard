import {
  ResponsiveContainer, BarChart, Bar,
  XAxis, YAxis, CartesianGrid, Tooltip,
} from "recharts";
import { COLORS, tooltipStyle, gridStyle, axisStyle } from "../lib/chartTheme";

export default function AppleWorkoutTypesChart({ data }) {
  const chartData = (data || []).slice(0, 10).map((d) => ({
    ...d,
    workout_type: d.workout_type.replace(/([A-Z])/g, " $1").trim(),
  }));

  return (
    <div className="bg-white/5 backdrop-blur border border-white/10 rounded-2xl p-5">
      <h3 className="text-sm font-medium text-gray-400 mb-4">Workout Types</h3>
      <ResponsiveContainer width="100%" height={280}>
        <BarChart data={chartData} layout="vertical">
          <CartesianGrid {...gridStyle} />
          <XAxis type="number" {...axisStyle} />
          <YAxis
            type="category"
            dataKey="workout_type"
            width={100}
            {...axisStyle}
            tick={{ fill: "#9ca3af", fontSize: 11 }}
          />
          <Tooltip
            {...tooltipStyle}
            formatter={(v) => [`${v} workouts`, "Count"]}
          />
          <Bar dataKey="count" fill={COLORS.appleGreen} radius={[0, 4, 4, 0]} barSize={16} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
