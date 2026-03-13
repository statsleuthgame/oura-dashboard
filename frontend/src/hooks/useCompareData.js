import { useState, useEffect, useRef } from "react";
import { fetchApi } from "../lib/api";
import { useDateRange } from "../context/DateRangeContext";
import { useUser } from "../context/UserContext";

/**
 * Fetches the same endpoint for both users and merges data by day.
 * Returns { data: [{ day, cody: value, stef: value }], loading, error }
 */
export function useCompareData(endpoint, valueKey) {
  const { days } = useDateRange();
  const { users } = useUser();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const valueKeyRef = useRef(valueKey);
  valueKeyRef.current = valueKey;

  useEffect(() => {
    if (users.length < 2) return;

    let cancelled = false;
    setLoading(true);
    setError(null);

    Promise.all(
      users.map((u) => fetchApi(endpoint, { days, user: u.key }))
    )
      .then((results) => {
        if (cancelled) return;

        const vk = valueKeyRef.current;
        const byDay = {};
        results.forEach((result, idx) => {
          const userKey = users[idx].key;
          const daily = result?.daily || [];
          for (const row of daily) {
            const day = row.day;
            if (!day) continue;
            if (!byDay[day]) byDay[day] = { day };
            byDay[day][userKey] = typeof vk === "function"
              ? vk(row)
              : row[vk];
          }
        });

        const merged = Object.values(byDay).sort((a, b) =>
          a.day.localeCompare(b.day)
        );
        setData(merged);
        setLoading(false);
      })
      .catch((err) => {
        if (!cancelled) {
          setError(err.message);
          setLoading(false);
        }
      });

    return () => { cancelled = true; };
  }, [endpoint, days, users]);

  return { data, loading, error };
}
