import http.client
import json
import pandas as pd
import time  # Import time for adding delays

# === CONFIGURATION ===
latitude = 43.0731       # Madison, WI
longitude = -89.4012
altitude = 264           # Approximate altitude of Madison, WI
start_year = 2000
end_year = 2024
output_file = "madison_precip_meteostat_2000_2024.csv"

# === DATA COLLECTION ===
all_data = []

headers = {
    'x-rapidapi-key': "77129d1f44msh6caedb88d5797c4p191e1cjsn34d06f9324a7",
    'x-rapidapi-host': "meteostat.p.rapidapi.com"
}

for year in range(start_year, end_year + 1):
    start_date = f"{year}-06-01"
    end_date = f"{year}-06-30"
    endpoint = f"/point/monthly?lat={latitude}&lon={longitude}&alt={altitude}&start={start_date}&end={end_date}"

    # Reinitialize the connection for each request
    conn = http.client.HTTPSConnection("meteostat.p.rapidapi.com")
    conn.request("GET", endpoint, headers=headers)
    res = conn.getresponse()

    if res.status == 429:  # Handle rate limit error
        print(f"Rate limit exceeded for year {year}. Retrying after delay...")
        time.sleep(5)  # Wait for 5 seconds before retrying
        continue

    if res.status != 200:
        print(f"Failed for year {year}: {res.status}")
        continue

    data = res.read()
    json_data = json.loads(data.decode("utf-8"))

    for record in json_data.get("data", []):
        all_data.append({
            "year": year,
            "date": record.get("date"),
            "precip_mm": record.get("prcp", 0)  # Assuming 'prcp' is the precipitation field
        })

    # Add a delay between requests to avoid hitting the rate limit
    time.sleep(1)  # Wait for 1 second between requests

# === SAVE TO CSV ===
df = pd.DataFrame(all_data)
df.to_csv(output_file, index=False)

print(f"✅ Saved {len(df)} records to {output_file}")