import { DateRangeProvider } from "./context/DateRangeContext";
import Layout from "./components/Layout";
import SleepDashboard from "./components/SleepDashboard";
import HrvReadinessPanel from "./components/HrvReadinessPanel";
import ActivityPanel from "./components/ActivityPanel";
import CorrelationsPanel from "./components/CorrelationsPanel";
import AppleHeartPanel from "./components/AppleHeartPanel";
import AppleActivityPanel from "./components/AppleActivityPanel";
import AppleSleepPanel from "./components/AppleSleepPanel";
import AppleWorkoutsPanel from "./components/AppleWorkoutsPanel";
import AppleVitalsPanel from "./components/AppleVitalsPanel";
import InsightsPanel from "./components/InsightsPanel";

export default function App() {
  return (
    <DateRangeProvider>
      <Layout>
        {/* AI Insights */}
        <InsightsPanel />

        {/* Oura Ring */}
        <div className="space-y-6">
          <div className="flex items-center gap-3">
            <div className="w-6 h-6 rounded-full bg-gradient-to-br from-oura-blue to-oura-purple flex items-center justify-center">
              <div className="w-3 h-3 rounded-full border-[1.5px] border-white/80" />
            </div>
            <h2 className="text-sm font-medium text-gray-500 uppercase tracking-wider">Oura Ring</h2>
          </div>
          <SleepDashboard />
          <HrvReadinessPanel />
          <ActivityPanel />
        </div>

        {/* Apple Health */}
        <div className="space-y-6 pt-4 border-t border-white/5">
          <div className="flex items-center gap-3">
            <div className="w-6 h-6 rounded-full bg-gradient-to-br from-apple-red to-apple-pink flex items-center justify-center text-white text-xs font-bold">
              <svg width="12" height="14" viewBox="0 0 12 14" fill="currentColor">
                <path d="M10.2 7.4c0-1.8 1.5-2.6 1.5-2.6s-0.8-1.2-2.1-1.2c-0.9 0-1.6 0.5-2.1 0.5s-1.1-0.5-1.8-0.5C4.2 3.6 2.7 4.8 2.7 7.4c0 1.6 0.6 3.3 1.4 4.4 0.6 0.9 1.2 1.7 2 1.7s1.1-0.5 1.8-0.5c0.8 0 1 0.5 1.8 0.5s1.3-0.8 1.9-1.6c0.4-0.5 0.6-1 0.6-1S10.2 9.8 10.2 7.4zM8.1 2.6c0.5-0.6 0.8-1.3 0.7-2.1-0.7 0-1.5 0.5-2 1.1-0.4 0.5-0.8 1.3-0.7 2 0.8 0.1 1.5-0.4 2-1z"/>
              </svg>
            </div>
            <h2 className="text-sm font-medium text-gray-500 uppercase tracking-wider">Apple Health</h2>
          </div>
          <AppleHeartPanel />
          <AppleSleepPanel />
          <AppleActivityPanel />
          <AppleWorkoutsPanel />
          <AppleVitalsPanel />
        </div>

        {/* Cross-source Correlations */}
        <div className="pt-4 border-t border-white/5">
          <CorrelationsPanel />
        </div>
      </Layout>
    </DateRangeProvider>
  );
}
