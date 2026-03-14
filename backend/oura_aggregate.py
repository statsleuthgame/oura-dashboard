"""Aggregate Oura daily data into weekly or monthly averages for long ranges."""

from collections import defaultdict
from datetime import date


def _group_key(day_str: str, level: str) -> str:
    dt = date.fromisoformat(day_str)
    if level == "monthly":
        return f"{dt.year}-{dt.month:02d}"
    return f"{dt.isocalendar()[0]}-{dt.isocalendar()[1]:02d}"


def aggregation_level(days: int) -> str:
    if days == 0 or days > 365:
        return "monthly"
    if days > 90:
        return "weekly"
    return "daily"


def group_oura_daily(rows: list, days: int, fields: list[str]) -> list:
    """Group a list of Pydantic models by week or month, averaging numeric fields.

    Returns the original list unchanged for daily aggregation.
    Fields listed are averaged; 'day' is taken from the first entry in each group.
    """
    level = aggregation_level(days)
    if level == "daily":
        return rows

    groups: dict[str, list] = defaultdict(list)
    for row in rows:
        key = _group_key(row.day, level)
        groups[key].append(row)

    # Detect which fields are int-typed on the model
    model_cls = type(rows[0])
    int_fields = set()
    for field in fields:
        annotation = model_cls.model_fields.get(field)
        if annotation and annotation.annotation in (int, int | None):
            int_fields.add(field)

    result = []
    for grp_key in sorted(groups):
        entries = groups[grp_key]
        grouped = {"day": entries[0].day}
        for field in fields:
            vals = [getattr(e, field) for e in entries if getattr(e, field) is not None]
            if not vals:
                grouped[field] = None
            elif field in int_fields:
                grouped[field] = round(sum(vals) / len(vals))
            else:
                grouped[field] = round(sum(vals) / len(vals), 1)
        result.append(model_cls(**grouped))

    return result
