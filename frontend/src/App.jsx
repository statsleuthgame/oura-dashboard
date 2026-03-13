import { DateRangeProvider } from "./context/DateRangeContext";
import { UserProvider } from "./context/UserContext";
import Layout from "./components/Layout";
import DashboardView from "./components/DashboardView";
import CompareView from "./components/CompareView";
import { useUser } from "./context/UserContext";

function AppContent() {
  const { view } = useUser();

  return (
    <Layout>
      {view === "compare" ? <CompareView /> : <DashboardView />}
    </Layout>
  );
}

export default function App() {
  return (
    <UserProvider>
      <DateRangeProvider>
        <AppContent />
      </DateRangeProvider>
    </UserProvider>
  );
}
