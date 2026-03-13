import { useDateRange } from "../context/DateRangeContext";

const options = [
  { value: 7, label: "7d" },
  { value: 30, label: "30d" },
  { value: 90, label: "90d" },
  { value: 365, label: "1y" },
  { value: 0, label: "All" },
];

export default function DateRangeSelector() {
  const { days, setDays } = useDateRange();

  return (
    <div className="flex gap-1 bg-white/5 rounded-lg p-1">
      {options.map((opt) => (
        <button
          key={opt.value}
          onClick={() => setDays(opt.value)}
          className={`px-3 py-1.5 text-sm font-medium rounded-md transition-all ${
            days === opt.value
              ? "bg-oura-blue text-white shadow-lg shadow-oura-blue/20"
              : "text-gray-400 hover:text-white hover:bg-white/5"
          }`}
        >
          {opt.label}
        </button>
      ))}
    </div>
  );
}
