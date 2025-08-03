import argparse
import os
from datetime import datetime, date
from dateutil import parser as dtparser
import pandas as pd
from providers.open_meteo import fetch_forecast

DEFAULT_CITIES = [
    {"city":"Jakarta","lat":-6.2000,"lon":106.8167},
    {"city":"Singapore","lat":1.3521,"lon":103.8198},
    {"city":"Tokyo","lat":35.6762,"lon":139.6503},
    {"city":"Sydney","lat":-33.8688,"lon":151.2093},
]

def load_cities(path: str|None):
    if path and os.path.exists(path):
        df = pd.read_csv(path)
        return df.to_dict(orient="records")
    return DEFAULT_CITIES

def parse_date(s: str|None) -> date:
    if not s:
        return date.today()
    return dtparser.parse(s).date()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", help="Forecast start date (YYYY-MM-DD). Default: today")
    ap.add_argument("--days", type=int, default=7, help="Number of days to fetch (default 7)")
    ap.add_argument("--cities", help="Path to CSV with columns: city,lat,lon")
    args = ap.parse_args()

    cities = load_cities(args.cities)
    start_date = parse_date(args.date)
    days = max(1, min(args.days, 16))

    rows = []
    for c in cities:
        daily = fetch_forecast(c["lat"], c["lon"], start_date, days)
        for rec in daily:
            rows.append({
                "date": rec["date"],
                "city": c["city"],
                "lat": c["lat"],
                "lon": c["lon"],
                "temp_max": rec["temp_max"],
                "temp_min": rec["temp_min"],
                "precipitation_sum": rec["precipitation_sum"],
            })

    df = pd.DataFrame(rows).sort_values(["city","date"]).reset_index(drop=True)

    os.makedirs("data/raw", exist_ok=True)
    os.makedirs("data/archive", exist_ok=True)
    out_path = os.path.join("data/raw", f"forecast_{start_date:%Y-%m-%d}.csv")
    df.to_csv(out_path, index=False, encoding="utf-8")
    ts_path = os.path.join("data/archive", f"forecast_{datetime.now():%Y-%m-%d_%H%M%S}.csv")
    df.to_csv(ts_path, index=False, encoding="utf-8")
    print(f"✅ Saved {len(df)} rows → {out_path}")
    print(f"🗄  Archived copy → {ts_path}")

if __name__ == "__main__":
    main()
