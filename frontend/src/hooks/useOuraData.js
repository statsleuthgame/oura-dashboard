import { useState, useEffect } from "react";
import { fetchApi } from "../lib/api";
import { useDateRange } from "../context/DateRangeContext";

export function useOuraData(endpoint) {
  const { days } = useDateRange();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);

    fetchApi(endpoint, { days })
      .then((result) => {
        if (!cancelled) {
          setData(result);
          setLoading(false);
        }
      })
      .catch((err) => {
        if (!cancelled) {
          setError(err.message);
          setLoading(false);
        }
      });

    return () => {
      cancelled = true;
    };
  }, [endpoint, days]);

  return { data, loading, error };
}
