import asyncio
from datetime import date, timedelta

import anthropic
from fastapi import APIRouter, Query, Request
from fastapi.responses import StreamingResponse

from config import get_settings
from apple_health_db import (
    query_daily_heart_rate, query_daily_hrv, query_daily_resting_hr,
    query_daily_steps, query_daily_energy, query_daily_sleep,
    query_daily_respiratory, query_daily_spo2,
)

router = APIRouter(prefix="/api")


def _summarize_list(rows, key, label):
    """Compute avg/min/max for a list of dicts."""
    vals = [r[key] for r in rows if r.get(key) is not None]
    if not vals:
        return None
    return {
        "label": label,
        "avg": round(sum(vals) / len(vals), 1),
        "min": round(min(vals), 1),
        "max": round(max(vals), 1),
        "days": len(vals),
    }


def _build_data_summary(oura_sleep, oura_readiness, oura_activity, apple_db, days, oura_sleep_scores=None):
    """Build a structured text summary of all health data for the prompt."""
    sections = []

    # Oura Sleep — aggregate by day first (multiple records per day = naps + main sleep)
    if oura_sleep:
        by_day: dict[str, dict] = {}
        for r in oura_sleep:
            day = r.get("day", "")
            if not day:
                continue
            if day not in by_day:
                by_day[day] = {"total": 0, "deep": 0, "efficiency": None, "max_dur": 0}
            total_sec = r.get("total_sleep_duration", 0) or 0
            by_day[day]["total"] += total_sec
            by_day[day]["deep"] += r.get("deep_sleep_duration", 0) or 0
            if total_sec > by_day[day]["max_dur"]:
                by_day[day]["efficiency"] = r.get("efficiency")
                by_day[day]["max_dur"] = total_sec

        total_sleeps = [round(d["total"] / 3600, 1) for d in by_day.values() if d["total"] > 0]
        deep_sleeps = [round(d["deep"] / 60, 1) for d in by_day.values() if d["deep"] > 0]
        efficiencies = [d["efficiency"] for d in by_day.values() if d["efficiency"] is not None]
        scores = []
        if oura_sleep_scores:
            scores = [oura_sleep_scores[day] for day in by_day if day in oura_sleep_scores and oura_sleep_scores[day] is not None]

        lines = [f"## Oura Sleep ({len(by_day)} nights)"]
        if scores:
            lines.append(f"- Sleep Score: avg {sum(scores)/len(scores):.0f}, range {min(scores)}-{max(scores)}")
        if total_sleeps:
            lines.append(f"- Total Sleep: avg {sum(total_sleeps)/len(total_sleeps):.1f}h, range {min(total_sleeps):.1f}-{max(total_sleeps):.1f}h")
        if deep_sleeps:
            lines.append(f"- Deep Sleep: avg {sum(deep_sleeps)/len(deep_sleeps):.0f}min, range {min(deep_sleeps):.0f}-{max(deep_sleeps):.0f}min")
        if efficiencies:
            lines.append(f"- Efficiency: avg {sum(efficiencies)/len(efficiencies):.0f}%, range {min(efficiencies)}-{max(efficiencies)}%")

        # Trend: compare last 7 days vs previous 7 days of total sleep
        sorted_days = sorted(by_day.keys())
        if len(sorted_days) >= 14:
            recent = [by_day[d]["total"] / 3600 for d in sorted_days[-7:]]
            prev = [by_day[d]["total"] / 3600 for d in sorted_days[-14:-7]]
            diff = sum(recent)/len(recent) - sum(prev)/len(prev)
            lines.append(f"- 7-day trend: {'up' if diff > 0 else 'down'} {abs(diff):.1f}h vs previous week")

        sections.append("\n".join(lines))

    # Oura Readiness
    if oura_readiness:
        scores = [r.get("score") for r in oura_readiness if r.get("score")]
        hrv_vals = [r.get("contributors", {}).get("hrv_balance") for r in oura_readiness]
        hrv_vals = [v for v in hrv_vals if v is not None]

        lines = ["## Oura Readiness"]
        if scores:
            lines.append(f"- Readiness Score: avg {sum(scores)/len(scores):.0f}, range {min(scores)}-{max(scores)}")
        if hrv_vals:
            lines.append(f"- HRV Balance: avg {sum(hrv_vals)/len(hrv_vals):.0f}, range {min(hrv_vals)}-{max(hrv_vals)}")

        if len(scores) >= 14:
            recent = scores[-7:]
            prev = scores[-14:-7]
            diff = sum(recent)/len(recent) - sum(prev)/len(prev)
            lines.append(f"- 7-day trend: {'up' if diff > 0 else 'down'} {abs(diff):.1f} points vs previous week")

        sections.append("\n".join(lines))

    # Oura Activity
    if oura_activity:
        steps_list = [r.get("steps") for r in oura_activity if r.get("steps")]
        cals = [r.get("active_calories") for r in oura_activity if r.get("active_calories")]

        lines = ["## Oura Activity"]
        if steps_list:
            lines.append(f"- Steps: avg {sum(steps_list)/len(steps_list):.0f}/day, range {min(steps_list)}-{max(steps_list)}")
        if cals:
            lines.append(f"- Active Calories: avg {sum(cals)/len(cals):.0f}/day")

        sections.append("\n".join(lines))

    # Apple Health data
    if apple_db is not None:
        hr_data = query_daily_heart_rate(apple_db, days)
        hrv_data = query_daily_hrv(apple_db, days)
        rhr_data = query_daily_resting_hr(apple_db, days)
        steps_data = query_daily_steps(apple_db, days)
        energy_data = query_daily_energy(apple_db, days)
        sleep_data = query_daily_sleep(apple_db, days)
        resp_data = query_daily_respiratory(apple_db, days)
        spo2_data = query_daily_spo2(apple_db, days)

        lines = [f"## Apple Health ({len(hr_data)} days of HR data)"]

        s = _summarize_list(hr_data, "avg_hr", "Avg Heart Rate")
        if s:
            lines.append(f"- Avg HR: {s['avg']} bpm (range {s['min']}-{s['max']})")

        s = _summarize_list(hrv_data, "avg_hrv", "HRV")
        if s:
            lines.append(f"- HRV (SDNN): avg {s['avg']}ms (range {s['min']}-{s['max']}ms)")

        s = _summarize_list(rhr_data, "resting_hr", "Resting HR")
        if s:
            lines.append(f"- Resting HR: avg {s['avg']} bpm (range {s['min']}-{s['max']})")

        if steps_data:
            step_vals = [r["value"] for r in steps_data if r.get("value")]
            if step_vals:
                lines.append(f"- Steps: avg {sum(step_vals)/len(step_vals):.0f}/day (range {min(step_vals):.0f}-{max(step_vals):.0f})")

        if sleep_data:
            totals = [r.get("total", 0) for r in sleep_data if r.get("total")]
            deeps = [r.get("deep", 0) for r in sleep_data if r.get("deep")]
            rems = [r.get("rem", 0) for r in sleep_data if r.get("rem")]
            if totals:
                lines.append(f"- Sleep: avg {sum(totals)/len(totals)/60:.1f}h/night ({len(totals)} nights)")
            if deeps:
                lines.append(f"- Deep Sleep: avg {sum(deeps)/len(deeps):.0f}min/night")
            if rems:
                lines.append(f"- REM Sleep: avg {sum(rems)/len(rems):.0f}min/night")

        s = _summarize_list(resp_data, "avg_rate", "Respiratory Rate")
        if s:
            lines.append(f"- Respiratory Rate: avg {s['avg']} breaths/min")

        s = _summarize_list(spo2_data, "avg_spo2", "SpO2")
        if s:
            lines.append(f"- SpO2: avg {s['avg']}% (min {s['min']}%)")

        if energy_data:
            active = [r.get("active_cal", 0) for r in energy_data if r.get("active_cal")]
            if active:
                lines.append(f"- Active Calories: avg {sum(active)/len(active):.0f}/day")

        # Trends for Apple Health (last 7 vs previous 7 daily values)
        if len(hr_data) >= 14:
            recent_hr = [r["avg_hr"] for r in hr_data[-7:] if r.get("avg_hr")]
            prev_hr = [r["avg_hr"] for r in hr_data[-14:-7] if r.get("avg_hr")]
            if recent_hr and prev_hr:
                diff = sum(recent_hr)/len(recent_hr) - sum(prev_hr)/len(prev_hr)
                lines.append(f"- HR 7-day trend: {'up' if diff > 0 else 'down'} {abs(diff):.1f} bpm vs previous week")

        if len(hrv_data) >= 14:
            recent_hrv = [r["avg_hrv"] for r in hrv_data[-7:] if r.get("avg_hrv")]
            prev_hrv = [r["avg_hrv"] for r in hrv_data[-14:-7] if r.get("avg_hrv")]
            if recent_hrv and prev_hrv:
                diff = sum(recent_hrv)/len(recent_hrv) - sum(prev_hrv)/len(prev_hrv)
                lines.append(f"- HRV 7-day trend: {'up' if diff > 0 else 'down'} {abs(diff):.1f}ms vs previous week")

        sections.append("\n".join(lines))

    return "\n\n".join(sections)


SYSTEM_PROMPT = """You are a health analytics expert analyzing personal health data from an Oura Ring and Apple Watch. \
Provide genuine, specific insights based on the data provided. Be direct and actionable.

Important context about this person:
- They have been taking Vyvanse (lisdexamfetamine) for almost a year. This is a stimulant medication \
that is known to elevate heart rate, reduce HRV, and can affect sleep. Factor this in when analyzing \
heart rate and HRV data — elevated resting HR and reduced HRV are expected side effects, not \
necessarily signs of poor cardiovascular fitness. Focus on trends and changes rather than absolute values \
for these metrics.

Guidelines:
- Reference specific numbers from the data
- Identify meaningful patterns, trends, and correlations
- Flag anything noteworthy (good or concerning)
- Suggest concrete, actionable improvements
- Keep it conversational but data-driven
- Use markdown formatting with headers and bullet points
- Do NOT add disclaimers about consulting doctors — the user knows this
- Keep your response to 4-6 focused insights, not a wall of text"""


@router.get("/insights")
async def get_insights(request: Request, days: int = Query(default=7, ge=0, le=2200), user: str = Query(default="cody")):
    from user_dep import get_oura, get_user_key
    settings = get_settings()

    if not settings.anthropic_api_key:
        return {"insights": None, "error": "No Anthropic API key configured. Add ANTHROPIC_API_KEY to your .env file."}

    key = get_user_key(request, user)
    profile = request.app.state.users[key]
    oura = profile["oura"]
    apple_db = profile["apple_db"]

    oura_days = days if days > 0 else 2200
    end_date = date.today().isoformat()
    start_date = (date.today() - timedelta(days=oura_days)).isoformat()

    # Fetch Oura data in parallel
    sleep_data, daily_sleep_data, readiness_data, activity_data = await asyncio.gather(
        oura.fetch("/v2/usercollection/sleep", start_date, end_date),
        oura.fetch("/v2/usercollection/daily_sleep", start_date, end_date),
        oura.fetch("/v2/usercollection/daily_readiness", start_date, end_date),
        oura.fetch("/v2/usercollection/daily_activity", start_date, end_date),
    )

    # Build sleep score lookup
    sleep_scores = {r.get("day"): r.get("score") for r in daily_sleep_data if r.get("day")}

    data_summary = _build_data_summary(sleep_data, readiness_data, activity_data, apple_db, days, sleep_scores)

    if not data_summary.strip():
        return {"insights": "Not enough data to generate insights. Try a longer time range."}

    range_label = f"last {days} days" if days > 0 else "all available data"
    user_name = profile["name"]

    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    def generate():
        with client.messages.stream(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=[{
                "role": "user",
                "content": f"Analyze {user_name}'s health data for the {range_label}. Today is {date.today().isoformat()}.\n\n{data_summary}",
            }],
        ) as stream:
            for text in stream.text_stream:
                yield text

    return StreamingResponse(generate(), media_type="text/plain")
