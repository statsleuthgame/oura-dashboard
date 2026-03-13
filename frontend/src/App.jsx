import { DateRangeProvider } from "./context/DateRangeContext";
import Layout from "./components/Layout";
import SleepDashboard from "./components/SleepDashboard";
import HrvReadinessPanel from "./components/HrvReadinessPanel";
import ActivityPanel from "./components/ActivityPanel";
import CorrelationsPanel from "./components/CorrelationsPanel";

export default function App() {
  return (
    <DateRangeProvider>
      <Layout>
        <SleepDashboard />
        <HrvReadinessPanel />
        <ActivityPanel />
        <CorrelationsPanel />
      </Layout>
    </DateRangeProvider>
  );
}
