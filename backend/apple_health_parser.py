import logging
import sqlite3
import time
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

RECORD_TYPE_MAP = {
    "HKQuantityTypeIdentifierHeartRate": "heart_rate",
    "HKQuantityTypeIdentifierHeartRateVariabilitySDNN": "hrv",
    "HKQuantityTypeIdentifierRestingHeartRate": "resting_heart_rate",
    "HKQuantityTypeIdentifierStepCount": "steps",
    "HKQuantityTypeIdentifierActiveEnergyBurned": "active_energy",
    "HKQuantityTypeIdentifierBasalEnergyBurned": "basal_energy",
    "HKCategoryTypeIdentifierSleepAnalysis": "sleep_analysis",
    "HKQuantityTypeIdentifierRespiratoryRate": "respiratory_rate",
    "HKQuantityTypeIdentifierOxygenSaturation": "oxygen_saturation",
    "HKQuantityTypeIdentifierWalkingHeartRateAverage": "walking_heart_rate",
    "HKQuantityTypeIdentifierFlightsClimbed": "flights_climbed",
    "HKQuantityTypeIdentifierDistanceWalkingRunning": "distance",
}

# Tables that store end_date
TABLES_WITH_END_DATE = {
    "steps", "active_energy", "basal_energy", "sleep_analysis",
    "flights_climbed", "distance",
}

SLEEP_VALUE_MAP = {
    "HKCategoryValueSleepAnalysisInBed": "InBed",
    "HKCategoryValueSleepAnalysisAsleepUnspecified": "Asleep",
    "HKCategoryValueSleepAnalysisAwake": "Awake",
    "HKCategoryValueSleepAnalysisAsleepCore": "AsleepCore",
    "HKCategoryValueSleepAnalysisAsleepDeep": "AsleepDeep",
    "HKCategoryValueSleepAnalysisAsleepREM": "AsleepREM",
}

BATCH_SIZE = 50_000


def parse_apple_date(date_str: str) -> str:
    """Convert '2024-03-15 14:30:00 -0700' to '2024-03-15 14:30:00'."""
    return date_str[:19]


def create_tables(conn: sqlite3.Connection):
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS parse_meta (
            key TEXT PRIMARY KEY,
            value TEXT
        );

        CREATE TABLE IF NOT EXISTS heart_rate (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            start_date TEXT NOT NULL,
            value REAL NOT NULL,
            source TEXT
        );
        CREATE INDEX IF NOT EXISTS idx_hr_date ON heart_rate(start_date);

        CREATE TABLE IF NOT EXISTS hrv (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            start_date TEXT NOT NULL,
            value REAL NOT NULL,
            source TEXT
        );
        CREATE INDEX IF NOT EXISTS idx_hrv_date ON hrv(start_date);

        CREATE TABLE IF NOT EXISTS resting_heart_rate (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            start_date TEXT NOT NULL,
            value REAL NOT NULL,
            source TEXT
        );
        CREATE INDEX IF NOT EXISTS idx_rhr_date ON resting_heart_rate(start_date);

        CREATE TABLE IF NOT EXISTS steps (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            value REAL NOT NULL,
            source TEXT
        );
        CREATE INDEX IF NOT EXISTS idx_steps_date ON steps(start_date);

        CREATE TABLE IF NOT EXISTS active_energy (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            value REAL NOT NULL,
            source TEXT
        );
        CREATE INDEX IF NOT EXISTS idx_ae_date ON active_energy(start_date);

        CREATE TABLE IF NOT EXISTS basal_energy (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            value REAL NOT NULL,
            source TEXT
        );
        CREATE INDEX IF NOT EXISTS idx_be_date ON basal_energy(start_date);

        CREATE TABLE IF NOT EXISTS sleep_analysis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            value TEXT NOT NULL,
            source TEXT
        );
        CREATE INDEX IF NOT EXISTS idx_sleep_date ON sleep_analysis(start_date);

        CREATE TABLE IF NOT EXISTS respiratory_rate (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            start_date TEXT NOT NULL,
            value REAL NOT NULL,
            source TEXT
        );
        CREATE INDEX IF NOT EXISTS idx_resp_date ON respiratory_rate(start_date);

        CREATE TABLE IF NOT EXISTS oxygen_saturation (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            start_date TEXT NOT NULL,
            value REAL NOT NULL,
            source TEXT
        );
        CREATE INDEX IF NOT EXISTS idx_spo2_date ON oxygen_saturation(start_date);

        CREATE TABLE IF NOT EXISTS walking_heart_rate (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            start_date TEXT NOT NULL,
            value REAL NOT NULL,
            source TEXT
        );
        CREATE INDEX IF NOT EXISTS idx_whr_date ON walking_heart_rate(start_date);

        CREATE TABLE IF NOT EXISTS flights_climbed (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            value REAL NOT NULL,
            source TEXT
        );
        CREATE INDEX IF NOT EXISTS idx_flights_date ON flights_climbed(start_date);

        CREATE TABLE IF NOT EXISTS distance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            value REAL NOT NULL,
            source TEXT
        );
        CREATE INDEX IF NOT EXISTS idx_dist_date ON distance(start_date);

        CREATE TABLE IF NOT EXISTS workouts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            workout_type TEXT NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            duration REAL,
            total_distance REAL,
            total_energy REAL,
            source TEXT
        );
        CREATE INDEX IF NOT EXISTS idx_workout_date ON workouts(start_date);
    """)


def parse_export(xml_path: str, db_path: str):
    """Stream-parse Apple Health export.xml into SQLite."""
    logger.info(f"Starting Apple Health parse: {xml_path} -> {db_path}")
    start_time = time.time()

    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")

    create_tables(conn)
    conn.execute(
        "INSERT OR REPLACE INTO parse_meta (key, value) VALUES ('status', 'in_progress')"
    )
    conn.commit()

    # Batch buffers per table
    buffers: dict[str, list[tuple]] = {table: [] for table in RECORD_TYPE_MAP.values()}
    buffers["workouts"] = []

    total_records = 0
    total_workouts = 0

    context = ET.iterparse(xml_path, events=("end",))
    _, root = next(context)

    for event, elem in context:
        if elem.tag == "Record":
            record_type = elem.get("type", "")
            table = RECORD_TYPE_MAP.get(record_type)
            if table:
                start_date = parse_apple_date(elem.get("startDate", ""))
                source = elem.get("sourceName", "")
                raw_value = elem.get("value", "")

                if table == "sleep_analysis":
                    value = SLEEP_VALUE_MAP.get(raw_value, raw_value)
                    end_date = parse_apple_date(elem.get("endDate", ""))
                    buffers[table].append((start_date, end_date, value, source))
                elif table in TABLES_WITH_END_DATE:
                    try:
                        value = float(raw_value)
                    except (ValueError, TypeError):
                        elem.clear()
                        root.clear()
                        continue
                    end_date = parse_apple_date(elem.get("endDate", ""))
                    buffers[table].append((start_date, end_date, value, source))
                else:
                    try:
                        value = float(raw_value)
                    except (ValueError, TypeError):
                        elem.clear()
                        root.clear()
                        continue
                    buffers[table].append((start_date, value, source))

                total_records += 1
                if total_records % BATCH_SIZE == 0:
                    _flush_buffers(conn, buffers)
                if total_records % 1_000_000 == 0:
                    logger.info(f"  Parsed {total_records:,} records...")

        elif elem.tag == "Workout":
            workout_type = elem.get("workoutActivityType", "")
            # Strip prefix
            workout_type = workout_type.replace("HKWorkoutActivityType", "")
            start_date = parse_apple_date(elem.get("startDate", ""))
            end_date = parse_apple_date(elem.get("endDate", ""))
            duration_min = _float_or_none(elem.get("duration"))
            duration_sec = duration_min * 60 if duration_min else None
            total_dist = _float_or_none(elem.get("totalDistance"))
            total_energy = _float_or_none(elem.get("totalEnergyBurned"))
            source = elem.get("sourceName", "")

            buffers["workouts"].append(
                (workout_type, start_date, end_date, duration_sec, total_dist, total_energy, source)
            )
            total_workouts += 1

        elem.clear()
        root.clear()

    # Flush remaining
    _flush_buffers(conn, buffers)

    # Mark complete
    now = datetime.now().isoformat()
    conn.execute(
        "INSERT OR REPLACE INTO parse_meta (key, value) VALUES ('status', 'complete')"
    )
    conn.execute(
        "INSERT OR REPLACE INTO parse_meta (key, value) VALUES ('parsed_at', ?)",
        (now,),
    )
    conn.execute(
        "INSERT OR REPLACE INTO parse_meta (key, value) VALUES ('total_records', ?)",
        (str(total_records),),
    )
    conn.commit()

    # Optimize
    conn.execute("ANALYZE")
    conn.close()

    elapsed = time.time() - start_time
    logger.info(
        f"Apple Health parse complete: {total_records:,} records, "
        f"{total_workouts:,} workouts in {elapsed:.1f}s"
    )


def _flush_buffers(conn: sqlite3.Connection, buffers: dict[str, list[tuple]]):
    for table, rows in buffers.items():
        if not rows:
            continue
        if table == "workouts":
            conn.executemany(
                "INSERT INTO workouts (workout_type, start_date, end_date, duration, total_distance, total_energy, source) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                rows,
            )
        elif table in TABLES_WITH_END_DATE:
            conn.executemany(
                f"INSERT INTO {table} (start_date, end_date, value, source) VALUES (?, ?, ?, ?)",
                rows,
            )
        else:
            conn.executemany(
                f"INSERT INTO {table} (start_date, value, source) VALUES (?, ?, ?)",
                rows,
            )
        rows.clear()
    conn.commit()


def _float_or_none(val: str | None) -> float | None:
    if val is None:
        return None
    try:
        return float(val)
    except (ValueError, TypeError):
        return None


def is_parsed(db_path: str) -> bool:
    """Check if the database exists and parsing is complete."""
    if not Path(db_path).exists():
        return False
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.execute(
            "SELECT value FROM parse_meta WHERE key = 'status'"
        )
        row = cursor.fetchone()
        conn.close()
        return row is not None and row[0] == "complete"
    except Exception:
        return False
