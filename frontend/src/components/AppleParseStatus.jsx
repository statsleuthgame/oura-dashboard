import { useState, useEffect } from "react";
import { fetchApi } from "../lib/api";

export default function AppleParseStatus() {
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchStatus = () => {
    fetchApi("/apple/parse/status")
      .then(setStatus)
      .catch(() => setStatus(null))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchStatus();
    const interval = setInterval(fetchStatus, 5000);
    return () => clearInterval(interval);
  }, []);

  const handleReparse = async () => {
    await fetch("/api/apple/parse", { method: "POST" });
    setStatus({ status: "parsing" });
  };

  if (loading || !status) return null;

  if (status.status === "complete") {
    return (
      <div className="flex items-center gap-2 text-xs text-gray-500">
        <div className="w-2 h-2 rounded-full bg-green-500" />
        <span>Apple Health loaded</span>
        {status.parsed_at && (
          <span className="text-gray-600">
            ({new Date(status.parsed_at).toLocaleDateString()})
          </span>
        )}
      </div>
    );
  }

  if (status.status === "in_progress" || status.status === "parsing") {
    return (
      <div className="flex items-center gap-2 text-xs text-yellow-500">
        <div className="w-2 h-2 rounded-full bg-yellow-500 animate-pulse" />
        <span>Parsing Apple Health data...</span>
      </div>
    );
  }

  return (
    <div className="flex items-center gap-2 text-xs text-gray-500">
      <div className="w-2 h-2 rounded-full bg-gray-500" />
      <span>Apple Health not loaded</span>
      <button
        onClick={handleReparse}
        className="text-oura-blue hover:underline"
      >
        Parse
      </button>
    </div>
  );
}
