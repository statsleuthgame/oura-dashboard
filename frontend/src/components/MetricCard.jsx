export default function MetricCard({ label, value, unit, color = "text-white" }) {
  return (
    <div className="bg-white/5 backdrop-blur border border-white/10 rounded-2xl p-5">
      <p className="text-sm text-gray-400 mb-1">{label}</p>
      <div className="flex items-baseline gap-1.5">
        <span className={`text-3xl font-bold tracking-tight ${color}`}>
          {value ?? "--"}
        </span>
        {unit && <span className="text-sm text-gray-500">{unit}</span>}
      </div>
    </div>
  );
}
