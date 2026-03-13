from pydantic import BaseModel


# --- Heart Rate ---

class AppleHeartRateDay(BaseModel):
    day: str
    avg_hr: float | None = None
    min_hr: float | None = None
    max_hr: float | None = None


class AppleHeartRateSummary(BaseModel):
    avg_hr: float | None = None
    min_hr: float | None = None
    max_hr: float | None = None
    total_days: int = 0


class AppleHeartRateResponse(BaseModel):
    summary: AppleHeartRateSummary
    daily: list[AppleHeartRateDay]


# --- HRV ---

class AppleHrvDay(BaseModel):
    day: str
    avg_hrv: float | None = None
    min_hrv: float | None = None
    max_hrv: float | None = None


class AppleHrvSummary(BaseModel):
    avg_hrv: float | None = None
    total_days: int = 0


class AppleHrvResponse(BaseModel):
    summary: AppleHrvSummary
    daily: list[AppleHrvDay]


# --- Resting Heart Rate ---

class AppleRestingHrDay(BaseModel):
    day: str
    resting_hr: float | None = None


class AppleRestingHrSummary(BaseModel):
    avg_resting_hr: float | None = None
    total_days: int = 0


class AppleRestingHrResponse(BaseModel):
    summary: AppleRestingHrSummary
    daily: list[AppleRestingHrDay]


# --- Steps ---

class AppleStepsDay(BaseModel):
    day: str
    steps: int = 0
    distance: float = 0
    flights: int = 0


class AppleStepsSummary(BaseModel):
    avg_daily_steps: float | None = None
    total_steps: int = 0
    avg_distance: float | None = None
    total_flights: int = 0


class AppleStepsResponse(BaseModel):
    summary: AppleStepsSummary
    daily: list[AppleStepsDay]


# --- Energy ---

class AppleEnergyDay(BaseModel):
    day: str
    active_cal: int = 0
    basal_cal: int = 0
    total_cal: int = 0


class AppleEnergySummary(BaseModel):
    avg_active_cal: float | None = None
    avg_basal_cal: float | None = None
    avg_total_cal: float | None = None


class AppleEnergyResponse(BaseModel):
    summary: AppleEnergySummary
    daily: list[AppleEnergyDay]


# --- Sleep ---

class AppleSleepDay(BaseModel):
    day: str
    core: float = 0
    deep: float = 0
    rem: float = 0
    awake: float = 0
    total_sleep: float = 0


class AppleSleepSummary(BaseModel):
    avg_total_sleep: float | None = None
    avg_deep: float | None = None
    avg_rem: float | None = None
    total_nights: int = 0


class AppleSleepResponse(BaseModel):
    summary: AppleSleepSummary
    daily: list[AppleSleepDay]


# --- Respiratory ---

class AppleRespiratoryDay(BaseModel):
    day: str
    avg_rate: float | None = None


class AppleRespiratorySummary(BaseModel):
    avg_respiratory_rate: float | None = None
    total_days: int = 0


class AppleRespiratoryResponse(BaseModel):
    summary: AppleRespiratorySummary
    daily: list[AppleRespiratoryDay]


# --- SpO2 ---

class AppleSpo2Day(BaseModel):
    day: str
    avg_spo2: float | None = None
    min_spo2: float | None = None


class AppleSpo2Summary(BaseModel):
    avg_spo2: float | None = None
    min_spo2: float | None = None
    total_days: int = 0


class AppleSpo2Response(BaseModel):
    summary: AppleSpo2Summary
    daily: list[AppleSpo2Day]


# --- Workouts ---

class AppleWorkout(BaseModel):
    workout_type: str
    start_date: str
    end_date: str
    duration: float | None = None
    total_distance: float | None = None
    total_energy: float | None = None
    source: str | None = None


class AppleWorkoutType(BaseModel):
    workout_type: str
    count: int
    total_duration: float | None = None
    total_calories: float | None = None


class AppleWorkoutsSummary(BaseModel):
    total_workouts: int = 0
    total_duration_min: float | None = None
    total_calories: float | None = None


class AppleWorkoutsResponse(BaseModel):
    summary: AppleWorkoutsSummary
    workouts: list[AppleWorkout]
    by_type: list[AppleWorkoutType]


# --- Parse Status ---

class AppleParseStatusResponse(BaseModel):
    status: str
    parsed_at: str | None = None
    total_records: str | None = None
    record_counts: dict[str, int] | None = None
