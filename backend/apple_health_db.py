import sqlite3
from datetime import date, timedelta


def get_connection(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def _date_range(days: int) -> tuple[str, str] | None:
    """Return (start_date, end_date) strings, or None if days=0 (all data)."""
    if days == 0:
        return None
    end = date.today() + timedelta(days=1)
    start = date.today() - timedelta(days=days)
    return start.isoformat(), end.isoformat()


def _aggregation_level(days: int) -> str:
    """Return 'daily', 'weekly', or 'monthly' based on the date range."""
    if days == 0 or days > 365:
        return "monthly"
    if days > 90:
        return "weekly"
    return "daily"


def _group_clause(days: int) -> str:
    level = _aggregation_level(days)
    if level == "monthly":
        return "strftime('%Y-%m', start_date)"
    if level == "weekly":
        return "strftime('%Y-%W', start_date)"
    return "DATE(start_date)"


def _day_select(days: int) -> str:
    """Return a SQL expression for the display date (proper date even for grouped)."""
    level = _aggregation_level(days)
    if level in ("weekly", "monthly"):
        return "MIN(DATE(start_date))"
    return "DATE(start_date)"


def _date_filter(days: int) -> tuple[str, tuple]:
    """Return (WHERE clause, params) for date filtering."""
    dr = _date_range(days)
    if dr is None:
        return "", ()
    return "WHERE start_date >= ? AND start_date < ?", dr


def query_daily_heart_rate(conn: sqlite3.Connection, days: int) -> list[dict]:
    group = _group_clause(days)
    day_sel = _day_select(days)
    where, params = _date_filter(days)
    rows = conn.execute(
        f"SELECT {day_sel} as day, AVG(value) as avg_hr, MIN(value) as min_hr, MAX(value) as max_hr "
        f"FROM heart_rate {where} GROUP BY {group} ORDER BY day",
        params,
    ).fetchall()
    return [dict(r) for r in rows]


def query_daily_hrv(conn: sqlite3.Connection, days: int) -> list[dict]:
    group = _group_clause(days)
    day_sel = _day_select(days)
    where, params = _date_filter(days)
    rows = conn.execute(
        f"SELECT {day_sel} as day, AVG(value) as avg_hrv, MIN(value) as min_hrv, MAX(value) as max_hrv "
        f"FROM hrv {where} GROUP BY {group} ORDER BY day",
        params,
    ).fetchall()
    return [dict(r) for r in rows]


def query_daily_resting_hr(conn: sqlite3.Connection, days: int) -> list[dict]:
    group = _group_clause(days)
    day_sel = _day_select(days)
    where, params = _date_filter(days)
    rows = conn.execute(
        f"SELECT {day_sel} as day, AVG(value) as resting_hr "
        f"FROM resting_heart_rate {where} GROUP BY {group} ORDER BY day",
        params,
    ).fetchall()
    return [dict(r) for r in rows]


def _source_dedup_sum(conn: sqlite3.Connection, table: str, days: int) -> list[dict]:
    """Sum by day+source, then take the max source total per day."""
    group = _group_clause(days)
    day_sel = _day_select(days)
    where, params = _date_filter(days)
    rows = conn.execute(
        f"SELECT MIN(grp_day) as day, MAX(src_total) as value FROM ("
        f"  SELECT {group} as grp, {day_sel} as grp_day, source, SUM(value) as src_total "
        f"  FROM {table} {where} GROUP BY grp, source"
        f") GROUP BY grp ORDER BY day",
        params,
    ).fetchall()
    return [dict(r) for r in rows]


def query_daily_steps(conn: sqlite3.Connection, days: int) -> list[dict]:
    steps = {r["day"]: r["value"] for r in _source_dedup_sum(conn, "steps", days)}
    dist = {r["day"]: r["value"] for r in _source_dedup_sum(conn, "distance", days)}
    flights = {r["day"]: r["value"] for r in _source_dedup_sum(conn, "flights_climbed", days)}

    all_days = sorted(set(steps) | set(dist) | set(flights))
    return [
        {
            "day": d,
            "steps": round(steps.get(d, 0)),
            "distance": round(dist.get(d, 0), 2),
            "flights": round(flights.get(d, 0)),
        }
        for d in all_days
    ]


def query_daily_energy(conn: sqlite3.Connection, days: int) -> list[dict]:
    active = {r["day"]: r["value"] for r in _source_dedup_sum(conn, "active_energy", days)}
    basal = {r["day"]: r["value"] for r in _source_dedup_sum(conn, "basal_energy", days)}

    all_days = sorted(set(active) | set(basal))
    return [
        {
            "day": d,
            "active_cal": round(active.get(d, 0)),
            "basal_cal": round(basal.get(d, 0)),
            "total_cal": round(active.get(d, 0) + basal.get(d, 0)),
        }
        for d in all_days
    ]


def query_daily_sleep(conn: sqlite3.Connection, days: int) -> list[dict]:
    """Reconstruct nightly sleep from stage segments."""
    where, params = _date_filter(days)
    rows = conn.execute(
        f"SELECT DATE(start_date) as night, value as stage, "
        f"SUM((JULIANDAY(end_date) - JULIANDAY(start_date)) * 24 * 60) as minutes "
        f"FROM sleep_analysis {where} GROUP BY night, stage ORDER BY night",
        params,
    ).fetchall()

    # Pivot stages into columns per night
    nights: dict[str, dict] = {}
    for r in rows:
        night = r["night"]
        if night not in nights:
            nights[night] = {"day": night, "in_bed": 0, "core": 0, "deep": 0, "rem": 0, "awake": 0, "asleep": 0}
        stage = r["stage"]
        minutes = round(r["minutes"], 1)

        if stage == "InBed":
            nights[night]["in_bed"] += minutes
        elif stage == "AsleepCore":
            nights[night]["core"] += minutes
        elif stage == "AsleepDeep":
            nights[night]["deep"] += minutes
        elif stage == "AsleepREM":
            nights[night]["rem"] += minutes
        elif stage == "Awake":
            nights[night]["awake"] += minutes
        elif stage in ("Asleep", "AsleepUnspecified"):
            nights[night]["asleep"] += minutes

    result = []
    for n in sorted(nights.values(), key=lambda x: x["day"]):
        n["total_sleep"] = round(n["core"] + n["deep"] + n["rem"] + n["asleep"], 1)
        result.append(n)

    # Aggregate if needed
    level = _aggregation_level(days)
    if level == "monthly" and len(result) > 90:
        return _grouped_avg_sleep(result, "monthly")
    if level == "weekly" and len(result) > 90:
        return _grouped_avg_sleep(result, "weekly")
    return result


def _grouped_avg_sleep(daily: list[dict], level: str) -> list[dict]:
    from collections import defaultdict
    groups: dict[str, list[dict]] = defaultdict(list)
    for d in daily:
        dt = date.fromisoformat(d["day"])
        if level == "monthly":
            key = f"{dt.year}-{dt.month:02d}"
        else:
            key = f"{dt.isocalendar()[0]}-{dt.isocalendar()[1]:02d}"
        groups[key].append(d)

    result = []
    for grp in sorted(groups):
        entries = groups[grp]
        n = len(entries)
        result.append({
            "day": entries[0]["day"],
            "core": round(sum(e["core"] for e in entries) / n, 1),
            "deep": round(sum(e["deep"] for e in entries) / n, 1),
            "rem": round(sum(e["rem"] for e in entries) / n, 1),
            "awake": round(sum(e["awake"] for e in entries) / n, 1),
            "total_sleep": round(sum(e["total_sleep"] for e in entries) / n, 1),
        })
    return result


def query_daily_respiratory(conn: sqlite3.Connection, days: int) -> list[dict]:
    group = _group_clause(days)
    day_sel = _day_select(days)
    where, params = _date_filter(days)
    rows = conn.execute(
        f"SELECT {day_sel} as day, AVG(value) as avg_rate "
        f"FROM respiratory_rate {where} GROUP BY {group} ORDER BY day",
        params,
    ).fetchall()
    return [dict(r) for r in rows]


def query_daily_spo2(conn: sqlite3.Connection, days: int) -> list[dict]:
    group = _group_clause(days)
    day_sel = _day_select(days)
    where, params = _date_filter(days)
    rows = conn.execute(
        f"SELECT {day_sel} as day, AVG(value * 100) as avg_spo2, MIN(value * 100) as min_spo2 "
        f"FROM oxygen_saturation {where} GROUP BY {group} ORDER BY day",
        params,
    ).fetchall()
    return [dict(r) for r in rows]


def query_workouts(conn: sqlite3.Connection, days: int) -> tuple[list[dict], list[dict]]:
    """Return (workouts_list, by_type_breakdown)."""
    where, params = _date_filter(days)

    workouts = conn.execute(
        f"SELECT workout_type, start_date, end_date, duration, total_distance, total_energy, source "
        f"FROM workouts {where} ORDER BY start_date DESC",
        params,
    ).fetchall()

    by_type = conn.execute(
        f"SELECT workout_type, COUNT(*) as count, SUM(duration) as total_duration, SUM(total_energy) as total_calories "
        f"FROM workouts {where} GROUP BY workout_type ORDER BY count DESC",
        params,
    ).fetchall()

    return [dict(r) for r in workouts], [dict(r) for r in by_type]


def query_parse_status(conn: sqlite3.Connection) -> dict:
    meta = {}
    for row in conn.execute("SELECT key, value FROM parse_meta").fetchall():
        meta[row["key"]] = row["value"]

    # Get record counts
    counts = {}
    tables = [
        "heart_rate", "hrv", "resting_heart_rate", "steps", "active_energy",
        "basal_energy", "sleep_analysis", "respiratory_rate", "oxygen_saturation",
        "flights_climbed", "distance", "workouts",
    ]
    for t in tables:
        row = conn.execute(f"SELECT COUNT(*) as c FROM {t}").fetchone()
        counts[t] = row["c"]

    return {
        "status": meta.get("status", "unknown"),
        "parsed_at": meta.get("parsed_at"),
        "total_records": meta.get("total_records"),
        "record_counts": counts,
    }
