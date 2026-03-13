import {
  ResponsiveContainer, BarChart, Bar,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend,
} from "recharts";
import { COLORS, tooltipStyle, gridStyle, axisStyle } from "../lib/chartTheme";
import { formatDate, formatNumber } from "../lib/formatters";

export default function AppleEnergyChart({ data }) {
  return (
    <div className="bg-white/5 backdrop-blur border border-white/10 rounded-2xl p-5">
      <h3 className="text-sm font-medium text-gray-400 mb-4">Energy Burned</h3>
      <ResponsiveContainer width="100%" height={240}>
        <BarChart data={data}>
          <CartesianGrid {...gridStyle} />
          <XAxis dataKey="day" tickFormatter={formatDate} {...axisStyle} />
          <YAxis {...axisStyle} />
          <Tooltip
            {...tooltipStyle}
            labelFormatter={formatDate}
            formatter={(v, name) => [
              `${formatNumber(Math.round(v))} cal`,
              name === "active_cal" ? "Active" : "Basal",
            ]}
          />
          <Legend wrapperStyle={{ fontSize: "12px", color: "#9ca3af" }} />
          <Bar dataKey="basal_cal" name="Basal" stackId="energy" fill={COLORS.orange} />
          <Bar dataKey="active_cal" name="Active" stackId="energy" fill={COLORS.appleRed} radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
