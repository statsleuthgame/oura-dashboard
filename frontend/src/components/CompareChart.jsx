import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from "recharts";
import { tooltipStyle, gridStyle, axisStyle } from "../lib/chartTheme";
import { formatDate } from "../lib/formatters";
import { useUser } from "../context/UserContext";

const USER_COLORS = {
  cody: "#4A90D9",
  stef: "#FF2D55",
};

export default function CompareChart({
  data,
  title,
  unit = "",
  domain,
  formatter,
}) {
  const { users } = useUser();

  if (!data || data.length === 0) {
    return (
      <div className="bg-white/5 backdrop-blur border border-white/10 rounded-2xl p-5">
        <h3 className="text-sm font-medium text-gray-400 mb-4">{title}</h3>
        <div className="h-[240px] flex items-center justify-center text-gray-600 text-sm">
          No data available
        </div>
      </div>
    );
  }

  const tooltipFormatter = (value) => {
    if (value == null) return "--";
    if (formatter) return formatter(value);
    return unit ? `${value}${unit}` : value;
  };

  return (
    <div className="bg-white/5 backdrop-blur border border-white/10 rounded-2xl p-5">
      <h3 className="text-sm font-medium text-gray-400 mb-4">{title}</h3>
      <ResponsiveContainer width="100%" height={260}>
        <LineChart data={data}>
          <CartesianGrid {...gridStyle} />
          <XAxis dataKey="day" tickFormatter={formatDate} {...axisStyle} />
          <YAxis domain={domain || ["auto", "auto"]} {...axisStyle} />
          <Tooltip
            {...tooltipStyle}
            labelFormatter={formatDate}
            formatter={tooltipFormatter}
          />
          <Legend
            wrapperStyle={{ color: "#9ca3af", fontSize: 13, paddingTop: 8 }}
          />
          {users.map((u) => (
            <Line
              key={u.key}
              type="monotone"
              dataKey={u.key}
              name={u.name}
              stroke={USER_COLORS[u.key] || "#888"}
              strokeWidth={2}
              dot={{ r: 2, fill: USER_COLORS[u.key] || "#888" }}
              activeDot={{ r: 5 }}
              connectNulls
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
