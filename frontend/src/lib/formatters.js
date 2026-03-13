export function formatMinutes(min) {
  if (min == null) return "--";
  const h = Math.floor(min / 60);
  const m = Math.round(min % 60);
  return h > 0 ? `${h}h ${m}m` : `${m}m`;
}

export function formatDate(iso) {
  if (!iso) return "";
  const d = new Date(iso + "T00:00:00");
  return d.toLocaleDateString("en-US", { month: "short", day: "numeric" });
}

export function roundTo(n, decimals = 1) {
  if (n == null) return "--";
  return Number(n.toFixed(decimals));
}

export function formatNumber(n) {
  if (n == null) return "--";
  return n.toLocaleString();
}
