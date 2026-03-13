from pydantic import BaseModel


class SleepDay(BaseModel):
    day: str
    score: int | None = None
    deep_sleep: float | None = None
    rem_sleep: float | None = None
    light_sleep: float | None = None
    total_sleep: float | None = None
    efficiency: int | None = None
    latency: float | None = None
    timing: float | None = None
    restfulness: float | None = None


class SleepSummary(BaseModel):
    avg_score: float | None = None
    avg_efficiency: float | None = None
    total_nights: int = 0


class SleepResponse(BaseModel):
    summary: SleepSummary
    daily: list[SleepDay]


class ReadinessDay(BaseModel):
    day: str
    score: int | None = None
    temperature_deviation: float | None = None
    hrv_balance: int | None = None
    resting_heart_rate: int | None = None
    body_temperature: int | None = None
    recovery_index: int | None = None
    sleep_balance: int | None = None
    activity_balance: int | None = None


class ReadinessSummary(BaseModel):
    avg_score: float | None = None
    avg_hrv_balance: float | None = None
    avg_resting_hr: float | None = None


class ReadinessResponse(BaseModel):
    summary: ReadinessSummary
    daily: list[ReadinessDay]


class ActivityDay(BaseModel):
    day: str
    score: int | None = None
    active_calories: int | None = None
    total_calories: int | None = None
    steps: int | None = None
    high_activity_time: float | None = None
    medium_activity_time: float | None = None
    low_activity_time: float | None = None
    equivalent_walking_distance: float | None = None


class ActivitySummary(BaseModel):
    avg_score: float | None = None
    total_steps: int = 0
    avg_calories: float | None = None
    total_active_minutes: float = 0


class ActivityResponse(BaseModel):
    summary: ActivitySummary
    daily: list[ActivityDay]


class HeartRatePoint(BaseModel):
    timestamp: str
    bpm: int


class HeartRateResponse(BaseModel):
    data: list[HeartRatePoint]


class CorrelationPair(BaseModel):
    metric_a: str
    metric_b: str
    r: float
    n: int


class CorrelationsResponse(BaseModel):
    pairs: list[CorrelationPair]
    matrix: dict[str, dict[str, float | None]]
