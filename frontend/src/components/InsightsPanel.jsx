import { useState, useEffect, useRef } from "react";
import { useDateRange } from "../context/DateRangeContext";
import { useUser } from "../context/UserContext";

export default function InsightsPanel() {
  const { days } = useDateRange();
  const { activeUser } = useUser();
  const [text, setText] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const abortRef = useRef(null);

  function fetchInsights() {
    if (abortRef.current) abortRef.current.abort();
    const controller = new AbortController();
    abortRef.current = controller;

    setLoading(true);
    setError(null);
    setText("");

    fetch(`/api/insights?days=${days}&user=${activeUser}`, { signal: controller.signal })
      .then((res) => {
        if (!res.ok) throw new Error(`API error ${res.status}`);
        const contentType = res.headers.get("content-type") || "";

        // JSON response means error or no-key
        if (contentType.includes("application/json")) {
          return res.json().then((data) => {
            if (data.error) {
              setError(data.error);
            } else if (data.insights) {
              setText(data.insights);
            }
            setLoading(false);
          });
        }

        // Streaming text response
        const reader = res.body.getReader();
        const decoder = new TextDecoder();
        let accumulated = "";

        function read() {
          return reader.read().then(({ done, value }) => {
            if (done) {
              setLoading(false);
              return;
            }
            accumulated += decoder.decode(value, { stream: true });
            setText(accumulated);
            return read();
          });
        }
        return read();
      })
      .catch((err) => {
        if (err.name !== "AbortError") {
          setError(err.message);
          setLoading(false);
        }
      });
  }

  useEffect(() => {
    return () => {
      if (abortRef.current) abortRef.current.abort();
    };
  }, []);

  // Simple markdown-ish rendering: headers, bold, bullets
  function renderMarkdown(md) {
    const lines = md.split("\n");
    const elements = [];
    let i = 0;

    for (const line of lines) {
      i++;
      if (line.startsWith("### ")) {
        elements.push(
          <h4 key={i} className="text-sm font-semibold text-white mt-4 mb-1">
            {line.slice(4)}
          </h4>
        );
      } else if (line.startsWith("## ")) {
        elements.push(
          <h3 key={i} className="text-base font-semibold text-white mt-5 mb-2">
            {line.slice(3)}
          </h3>
        );
      } else if (line.startsWith("- ") || line.startsWith("* ")) {
        elements.push(
          <li key={i} className="text-sm text-gray-300 ml-4 list-disc mb-1">
            {renderInline(line.slice(2))}
          </li>
        );
      } else if (line.trim() === "") {
        elements.push(<div key={i} className="h-2" />);
      } else {
        elements.push(
          <p key={i} className="text-sm text-gray-300 mb-1">
            {renderInline(line)}
          </p>
        );
      }
    }
    return elements;
  }

  function renderInline(text) {
    // Bold **text**
    const parts = text.split(/(\*\*[^*]+\*\*)/g);
    return parts.map((part, i) => {
      if (part.startsWith("**") && part.endsWith("**")) {
        return (
          <strong key={i} className="text-white font-medium">
            {part.slice(2, -2)}
          </strong>
        );
      }
      return part;
    });
  }

  return (
    <section className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-white">AI Insights</h2>
        <button
          onClick={fetchInsights}
          disabled={loading}
          className="px-4 py-1.5 text-sm font-medium rounded-lg bg-gradient-to-r from-purple-500 to-blue-500 text-white hover:from-purple-400 hover:to-blue-400 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
        >
          {loading ? "Analyzing..." : text ? "Refresh" : "Generate Insights"}
        </button>
      </div>

      {error && (
        <div className="bg-red-500/10 border border-red-500/20 rounded-2xl p-5">
          <p className="text-red-400 text-sm">{error}</p>
        </div>
      )}

      {!text && !loading && !error && (
        <div className="bg-white/5 backdrop-blur border border-white/10 rounded-2xl p-8 text-center">
          <p className="text-gray-500 text-sm">
            Click "Generate Insights" to get AI-powered analysis of your health data for the selected time range.
          </p>
        </div>
      )}

      {(text || loading) && (
        <div className="bg-white/5 backdrop-blur border border-white/10 rounded-2xl p-6">
          {text && <div>{renderMarkdown(text)}</div>}
          {loading && !text && (
            <div className="flex items-center gap-3">
              <div className="w-4 h-4 border-2 border-purple-400 border-t-transparent rounded-full animate-spin" />
              <span className="text-sm text-gray-400">Analyzing your health data...</span>
            </div>
          )}
          {loading && text && (
            <div className="mt-2">
              <div className="w-2 h-4 bg-purple-400 inline-block animate-pulse rounded-sm" />
            </div>
          )}
        </div>
      )}
    </section>
  );
}
