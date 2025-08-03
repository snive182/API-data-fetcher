import requests
from datetime import date, timedelta
from typing import List, Dict

def fetch_forecast(lat: float, lon: float, start_date: date, days: int) -> List[Dict]:
    end_date = start_date + timedelta(days=days-1)
    base = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
        "timezone": "auto",
    }
    r = requests.get(base, params=params, timeout=30)
    r.raise_for_status()
    js = r.json()
    daily = js.get("daily", {})
    dates = daily.get("time", []) or []
    tmax = daily.get("temperature_2m_max", []) or []
    tmin = daily.get("temperature_2m_min", []) or []
    prcp = daily.get("precipitation_sum", []) or []
    out = []
    for i in range(len(dates)):
        out.append({
            "date": dates[i],
            "temp_max": tmax[i] if i < len(tmax) else None,
            "temp_min": tmin[i] if i < len(tmin) else None,
            "precipitation_sum": prcp[i] if i < len(prcp) else None,
        })
    return out
