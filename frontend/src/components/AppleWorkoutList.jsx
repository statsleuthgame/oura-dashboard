import { formatDate, formatWorkoutDuration } from "../lib/formatters";

export default function AppleWorkoutList({ workouts }) {
  const items = (workouts || []).slice(0, 20);

  return (
    <div className="bg-white/5 backdrop-blur border border-white/10 rounded-2xl p-5">
      <h3 className="text-sm font-medium text-gray-400 mb-4">Recent Workouts</h3>
      <div className="space-y-2 max-h-[320px] overflow-y-auto">
        {items.map((w, i) => {
          const typeName = w.workout_type.replace(/([A-Z])/g, " $1").trim();
          return (
            <div
              key={i}
              className="flex items-center justify-between py-2 px-3 rounded-lg bg-white/[0.03] hover:bg-white/[0.06] transition-colors"
            >
              <div>
                <p className="text-sm text-white font-medium">{typeName}</p>
                <p className="text-xs text-gray-500">
                  {formatDate(w.start_date?.slice(0, 10))}
                </p>
              </div>
              <div className="text-right">
                <p className="text-sm text-gray-300">
                  {formatWorkoutDuration(w.duration)}
                </p>
                {w.total_energy && (
                  <p className="text-xs text-gray-500">
                    {Math.round(w.total_energy)} cal
                  </p>
                )}
              </div>
            </div>
          );
        })}
        {items.length === 0 && (
          <p className="text-gray-600 text-sm text-center py-4">No workouts found</p>
        )}
      </div>
    </div>
  );
}
