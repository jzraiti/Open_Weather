import requests
import pandas as pd
from datetime import datetime

# === CONFIGURATION ===
latitude = 43.0731       # Madison, WI
longitude = -89.4012
start_day = "06-01"
end_day = "06-30"
start_year = 2000
end_year = 2024
output_file = "madison_precip_2000_2024.csv"

# === DATA COLLECTION ===
all_data = []

for year in range(start_year, end_year + 1):
    start_date = f"{year}-{start_day}"
    end_date = f"{year}-{end_day}"

    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": start_date,
        "end_date": end_date,
        "daily": "precipitation_sum",
        "timezone": "auto"
    }

    response = requests.get(url, params=params)
    if response.status_code != 200:
        print(f"Failed for year {year}: {response.status_code}")
        continue

    json_data = response.json()
    dates = json_data.get("daily", {}).get("time", [])
    precipitation = json_data.get("daily", {}).get("precipitation_sum", [])

    for date, prcp in zip(dates, precipitation):
        all_data.append({
            "year": year,
            "date": date,
            "precip_mm": prcp
        })

# === SAVE TO CSV ===
df = pd.DataFrame(all_data)
df.to_csv(output_file, index=False)

print(f"✅ Saved {len(df)} records to {output_file}")
