import DateRangeSelector from "./DateRangeSelector";

export default function Layout({ children }) {
  return (
    <div className="min-h-screen bg-[#0F1117]">
      <header className="sticky top-0 z-10 backdrop-blur-xl bg-[#0F1117]/80 border-b border-white/5">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-oura-blue to-oura-purple flex items-center justify-center">
              <div className="w-4 h-4 rounded-full border-2 border-white/80" />
            </div>
            <h1 className="text-xl font-semibold text-white tracking-tight">
              Oura Dashboard
            </h1>
          </div>
          <DateRangeSelector />
        </div>
      </header>
      <main className="max-w-7xl mx-auto px-4 sm:px-6 py-6 space-y-6">
        {children}
      </main>
    </div>
  );
}
