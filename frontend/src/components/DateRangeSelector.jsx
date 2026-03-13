import { useDateRange } from "../context/DateRangeContext";

const options = [7, 30, 90];

export default function DateRangeSelector() {
  const { days, setDays } = useDateRange();

  return (
    <div className="flex gap-1 bg-white/5 rounded-lg p-1">
      {options.map((d) => (
        <button
          key={d}
          onClick={() => setDays(d)}
          className={`px-3 py-1.5 text-sm font-medium rounded-md transition-all ${
            days === d
              ? "bg-oura-blue text-white shadow-lg shadow-oura-blue/20"
              : "text-gray-400 hover:text-white hover:bg-white/5"
          }`}
        >
          {d}d
        </button>
      ))}
    </div>
  );
}
