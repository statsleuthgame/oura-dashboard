import { useState, useEffect } from "react";
import { fetchApi } from "../lib/api";
import { useDateRange } from "../context/DateRangeContext";
import { useUser } from "../context/UserContext";

export function useOuraData(endpoint) {
  const { days } = useDateRange();
  const { activeUser } = useUser();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);

    fetchApi(endpoint, { days, user: activeUser })
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
  }, [endpoint, days, activeUser]);

  return { data, loading, error };
}
